from typing import List, Optional

from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.schemas import WorkerState, WorkerType


def get_worker(db: Session, worker_id: int) -> schemas.Worker:
    return db.query(models.Worker).filter(models.Worker.worker_id == worker_id).first()


def get_workers(db: Session, skip: int = 0, limit: int = 100,
                worker_type: Optional[WorkerType] = None,
                worker_state: Optional[WorkerState] = None) -> List[schemas.Worker]:

    query_stm = db.query(models.Worker)

    if worker_state:
        query_stm.filter(models.Worker.state == worker_state)

    if worker_type:
        query_stm.filter(models.Worker.type == worker_type)

    return query_stm.offset(skip).limit(limit).all()