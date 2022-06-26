import logging
from typing import Optional

import socketio
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.crud.jobs_read import get_job, on_job_queue_order_changes
from donkeycarmanager.emitters.jobs import on_job_update
from donkeycarmanager.emitters.jobs_without_job_sched import on_job_change_worker_notify
from donkeycarmanager.helpers.utils import dict_to_attr
from donkeycarmanager.schemas import JobState
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler

RANKING_STEP = 2000  # How much place by default between 2 players.py in driving waiting queue

logger = logging.getLogger(__name__)


async def create_job(db: Session, sio: socketio.AsyncServer, job_sched: AsyncJobScheduler,
                     job: schemas.Job)-> schemas.Job:
    # Find ranking number
    last_job: Optional[models.Job] = db.query(models.Job).\
        order_by(desc(models.Job.rank)).limit(1).first()
    new_rank = last_job.rank + RANKING_STEP if last_job else RANKING_STEP  # Don't start at 0

    db_job = models.Job(**job.dict(), rank=new_rank)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    await on_job_change_worker_notify(db=db, sio=sio, job_changed=db_job)
    await on_job_queue_order_changes(db=db, sio=sio, jobs_changed=[db_job])  # Notify the queue was changed

    await job_sched.on_job_changed(db_job)

    return db_job


async def update_job(db: Session, sio: socketio.AsyncServer, job_sched: AsyncJobScheduler,
                     job: schemas.Job) -> schemas.Job:
    # TODO : fail for non coherent changes, such as :
    # - change in state from CANCELLING or CANCELLED to waiting
    # - worker change as the job is running ...

    db_job = get_job(db=db, job_id=job.job_id)
    dict_to_attr(db_job, job.dict())
    db.commit()
    db.refresh(db_job)

    await on_job_update(db, sio, job_sched, db_job)

    return db_job


async def update_job_state(db: Session, sio: socketio.AsyncServer, job_sched: AsyncJobScheduler,
                           job_id: int, job_state: JobState) -> schemas.Job:
    db_job = get_job(db=db, job_id=job_id)
    db_job.state = job_state
    db.commit()

    await on_job_update(db, sio, job_sched, db_job)

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
    await on_job_queue_order_changes(db, sio, jobs_changed=[to_move])

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
    await on_job_queue_order_changes(db, sio, jobs_changed=[to_move])

    print(f'Moved {to_move.job_id} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {after_item.job_id} ({after_item.rank})')
    return to_move
