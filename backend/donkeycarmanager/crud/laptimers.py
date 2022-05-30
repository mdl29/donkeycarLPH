from typing import List

from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr


def get_laptimer(db: Session, laptimer_id: str) -> schemas.LapTimer:
    return db.query(models.LapTimer).filter(models.LapTimer.laptimer_id == laptimer_id).first()


def get_laptimers(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.LapTimer]:
    return db.query(models.LapTimer).offset(skip).limit(limit).all()


def create_laptimer(db: Session, laptimer: schemas.LapTimerCreate) -> schemas.LapTimer:
    db_laptimer = models.LapTimer(**laptimer.dict())
    db.add(db_laptimer)
    db.commit()
    db.refresh(db_laptimer)
    return db_laptimer


def update_laptimer(db: Session, laptimer: schemas.LapTimerUpdate) -> schemas.LapTimer:
    db_laptimer = get_laptimer(db=db, laptimer_id=laptimer.laptimer_id)
    dict_to_attr(db_laptimer, laptimer.dict())
    db.commit()
    db.refresh(db_laptimer)
    return db_laptimer
