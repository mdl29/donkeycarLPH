from typing import List

from sqlalchemy.orm import Session
from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr


def get_worker(db: Session, worker_id: int) -> schemas.Worker:
    return db.query(models.Worker).filter(models.Worker.worker_id == worker_id).first()


def get_workers(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Worker]:
    return db.query(models.Worker).offset(skip).limit(limit).all()


def create_worker(db: Session, worker: schemas.Worker) -> schemas.Worker:
    db_worker = models.Worker(**worker.dict())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    return db_worker


def update_worker(db: Session, worker: schemas.Worker) -> schemas.Worker:
    db_worker = get_worker(db=db, worker_id=worker.worker_id)
    dict_to_attr(db_worker, worker.dict())
    db.commit()
    db.refresh(db_worker)
    return db_worker
