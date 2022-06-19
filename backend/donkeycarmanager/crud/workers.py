from sqlalchemy import or_
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.crud.workers_read import get_worker
from donkeycarmanager.helpers.utils import dict_to_attr
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler


def create_worker(db: Session, worker: schemas.Worker) -> schemas.Worker:
    db_worker = models.Worker(**worker.dict())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


async def update_worker(db: Session, worker: schemas.Worker, job_sched: AsyncJobScheduler) -> schemas.Worker:
    db_worker = get_worker(db=db, worker_id=worker.worker_id)
    dict_to_attr(db_worker, worker.dict())
    db.commit()
    db.refresh(db_worker)

    await job_sched.on_worker_changed(worker)
    return db_worker

def clean_jobs(db: Session, worker_id: str, fail_details: str):
    res = db.query(models.Job)\
        .filter(models.Job.worker_id == worker_id,
                or_(models.Job.state == schemas.JobState.RUNNING,
                    models.Job.state == schemas.JobState.PAUSED,
                    models.Job.state == schemas.JobState.PAUSING,
                    models.Job.state == schemas.JobState.RESUMING,
                    models.Job.state == schemas.JobState.CANCELLING))\
        .update({models.Job.state: schemas.JobState.FAILED,
                 models.Job.fail_details: fail_details})
    db.commit()
    return res
