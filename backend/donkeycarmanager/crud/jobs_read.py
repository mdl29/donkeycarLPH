# Created du to circular import with scheduler
import logging
import socketio
import json
from typing import List, Optional

from sqlalchemy import asc
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.schemas import JobState, WorkerType, EventJobQueue, EventJobChanged

logger = logging.getLogger(__name__)

async def on_job_queue_order_changes(db: Session, sio: socketio.AsyncServer,
                                     jobs_changed: List[models.Job] = []) -> None:
    """
    Handle executed each time the job queue changes order changes.
    Sends an event to socket IO with the new list.
    :param db: Database.
    :param sio: Socket IO server.
    :param jobs_changed: List of jobs that were changed, used to specifically notify on cars queues
    """
    logger.debug(
        "on_job_queue_order_changes: going to notify of job changes, number of changed job: %i", len(jobs_changed))

    # Send socket IO event with all queue elements
    db_queue = get_jobs(db=db, by_rank=True)
    event = EventJobQueue(jobs=db_queue)
    event_json_payload = json.loads(event.json()) # Workaround to get pydantic deep conversion as dict
    logger.debug('on_job_queue_all_change: emitting "jobs.all.updated" with a number of %i jobs', len(db_queue))
    await sio.emit('jobs.all.updated',event_json_payload)

    # Notify all workers gets with all of their jobs
    jobs_changed_with_workers = filter(lambda j: j.worker_id is not None, jobs_changed)
    job_changed_worker_ids = map(lambda j: j.worker_id, jobs_changed_with_workers)

    for worker_id in job_changed_worker_ids:
        if worker_id is not None:
            jobs_by_rank = get_jobs(db, worker_id=worker_id, by_rank=True)
            event = EventJobQueue(jobs=jobs_by_rank)
            event_json_payload = json.loads(event.json()) # Workaround to get pydantic deep conversion as dict
            event_name = f'jobs.{worker_id}.updated'
            logger.debug('on_job_queue_all_change: emitting "%s"', event_name)
            await sio.emit(event_name,
                           event_json_payload)


async def on_job_change_worker_notify(db: Session, sio: socketio.AsyncServer,
                                      job_changed: models.Job) -> None:
    """
    Emit to notify a worker of "one" job change. Shouldn't be used to handle jobs orders.
    :param db: database
    :param sio: socketIO
    :param job_changed: Changed job.
    """
    if job_changed.worker_id is None:
        return

    # Send socket IO event with all queue elements
    event = EventJobChanged(job=job_changed)
    event_json_payload = json.loads(event.json())  # Workaround to get pydantic deep conversion as dict
    event_name = f"one_job.{job_changed.worker_id}.updated"
    logger.debug('on_one_job_change: emitting "%s" with : %s', event_name, event_json_payload)
    await sio.emit(event_name, event_json_payload)


def get_job(db: Session, job_id: int) -> schemas.Job:
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()


def get_jobs(db: Session, skip: int = 0, limit: int = 100,
             worker_id: Optional[int] = None,
             no_worker: Optional[bool] = None,
             worker_type: Optional[WorkerType] = None,
             job_state: Optional[JobState] = None,
             by_rank: bool = True) -> List[schemas.Job]:
    query_stm = db.query(models.Job)

    if by_rank:
        query_stm = query_stm.order_by(asc(models.Job.rank))

    if worker_id:
        query_stm = query_stm.filter(models.Job.worker_id == worker_id)

    if no_worker:
        query_stm = query_stm.filter(models.Job.worker_id == None)

    if worker_type:
        query_stm = query_stm.filter(models.Job.worker_type == worker_type)

    if job_state:
        query_stm = query_stm.filter(models.Job.state == job_state)

    return query_stm.offset(skip).limit(limit).all()