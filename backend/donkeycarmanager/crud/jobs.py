import logging

import socketio
import json
from typing import List, Optional, Dict

from sqlalchemy.orm import Session
from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr
from sqlalchemy import desc, asc, literal_column

from donkeycarmanager.schemas import EventJobQueue

RANKING_STEP = 2000  # How much place by default between 2 players.py in driving waiting queue

logger = logging.getLogger(__name__)

async def on_job_queue_all_change(db: Session, sio: socketio.AsyncServer,
                                  jobs_changed: List[models.Job] = []) -> None:
    """
    Handle executed each time the player driving waiting queue changes.
    Sends an event to socket IO with the new list.
    :param db: Database.
    :param sio: Socket IO server.
    :param jobs_changed: List of jobs that were changed, used to specifically notify on cars queues
    """
    logger.debug(
        "on_job_queue_all_change: going to notify of job changes, number of changed job: %i", len(jobs_changed))

    # Send socket IO event with all queue elements
    db_queue = get_jobs(db=db, by_rank=True)
    event = EventJobQueue(jobs=db_queue)
    event_json_payload = json.loads(event.json())
    logger.debug('on_job_queue_all_change: emitting "jobs.all.updated" with : %s', event_json_payload)
    await sio.emit('jobs.all.updated',event_json_payload)  # Workaround to get pydantic deep conversion as dict

    # Notify all workers gets with all of their jobs
    jobs_changed_with_workers = filter(lambda j: j.worker_id != None, jobs_changed)
    job_changed_worker_ids = map(lambda j: j.worker_id, jobs_changed_with_workers)

    for worker_id in job_changed_worker_ids:
        if worker_id is not None:
            jobs_by_rank = get_jobs(db, worker_id=worker_id, by_rank=True)
            event = EventJobQueue(jobs=jobs_by_rank)
            event_json_payload = json.loads(event.json())
            event_name = f'jobs.{worker_id}.updated'
            logger.debug('on_job_queue_all_change: emitting "%s" with : %s', event_name, event)
            await sio.emit(event_name,
                           event_json_payload)  # Workaround to get pydantic deep conversion as dict


def get_job(db: Session, job_id: int) -> schemas.Job:
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()


def get_jobs(db: Session, skip: int = 0, limit: int = 100,
             worker_id: Optional[int] = None,
             by_rank: bool = True) -> List[schemas.Job]:
    query_stm = db.query(models.Job)

    if by_rank:
        query_stm = query_stm.order_by(asc(models.Job.rank))

    if worker_id:
        query_stm = query_stm.filter(models.Job.worker_id == worker_id)

    return query_stm.offset(skip).limit(limit).all()


async def create_job(db: Session, sio: socketio.AsyncServer, job: schemas.Job)-> schemas.Job:
    # Find ranking number
    last_job: Optional[models.Job] = db.query(models.Job).\
        order_by(desc(models.Job.rank)).limit(1).first()
    new_rank = last_job.rank + RANKING_STEP if last_job else RANKING_STEP  # Don't start at 0

    db_job = models.Job(**job.dict(), rank=new_rank)
    db.add(db_job)
    db.commit()
    await on_job_queue_all_change(db=db, sio=sio, jobs_changed=[db_job])  # Notify the queue was changed

    db.refresh(db_job)

    return db_job


async def update_job(db: Session, sio: socketio.AsyncServer, job: schemas.Job) -> schemas.Job:
    db_job = get_job(db=db, job_id=job.job_id)
    dict_to_attr(db_job, job.dict())
    db.commit()
    db.refresh(db_job)

    await on_job_queue_all_change(db, sio, jobs_changed=[db_job])

    return db_job


async def move_job_after_another_in_queue(db: Session,
                                          sio: socketio.AsyncServer,
                                          to_move: models.Job,
                                          before_item: models.Job) -> schemas.Job:
    """
    Move job waiting queue item (to_move) after another job waiting queue item.
    :param db: Database
    :param sio: SocketIO
    :param to_move: job that will be moved.
    :param before_item: Reference job, will end before the player that should be moved.
    :return: Moved job.
    """
    old_rank = to_move.rank

    # Find the first queued element after the player, the one that is the next after him
    existing_job_after = db.query(models.Job).filter(models.Job.rank > before_item.rank)\
        .order_by(asc(models.Job.rank))\
        .limit(1).first()

    if existing_job_after:
        if existing_job_after.job_id == to_move.job_id:  # No need to move it, it's already after
            return to_move

        delta = existing_job_after.rank - before_item.rank
        if delta > 0:
            to_move.rank = before_item.rank + delta // 2
        else:
            raise ValueError('Impossible to rank this player no values left')
    else:  # No one after the referenced player, simply putting our player here with the RANKING_STEP
        to_move.rank = before_item.rank + RANKING_STEP

    db.commit()
    await on_job_queue_all_change(db, sio, jobs_changed=[to_move])

    print(f'Moved {to_move.job_id} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {before_item.job_id} ({before_item.rank})')
    return to_move


async def move_job_before_another_queue(db: Session,
                                        sio: socketio.AsyncServer,
                                        to_move: models.Job,
                                        after_item: models.Job) -> schemas.Job:
    """
    Move job waiting queue item (to_move) before another job waiting queue item.
    :param db: Database
    :param sio: SocketIO
    :param to_move: job that will be moved.
    :param after_item: Reference job, will end after the player that should be moved.
    :return: The moved job.
    """
    old_rank = to_move.rank

    # Find the first queued element after the player, the one that is the next after him
    existing_job_before = db.query(models.Job).filter(
        models.Job.rank < after_item.rank) \
        .order_by(desc(models.Job.rank)) \
        .limit(1).first()

    if existing_job_before:
        if existing_job_before.job_id == to_move.player_id:  # No need to move it, it's already after
            return to_move

        delta = after_item.rank - existing_job_before.rank
        if delta > 0:
            to_move.rank = after_item.rank - delta // 2
        else:
            raise ValueError('Impossible to rank this player no values left')
    else:  # No one after the referenced player, simply putting our player here with the RANKING_STEP
        to_move.rank = after_item.rank // 2  # Let some place behind it and before it

    db.commit()
    await on_job_queue_all_change(db, sio, jobs_changed=[to_move])

    print(f'Moved {to_move.job_id} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {after_item.job_id} ({after_item.rank})')
    return to_move
