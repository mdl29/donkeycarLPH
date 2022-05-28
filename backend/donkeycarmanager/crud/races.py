from typing import List

from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr


def get_race(db: Session, race_id: int) -> schemas.Race:
    return db.query(models.Car).filter(models.Race.race_id == race_id).first()


def get_races(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Race]:
    return db.query(models.Race).offset(skip).limit(limit).all()


def create_race(db: Session, race: schemas.Race) -> schemas.Race:
    db_race = models.Race(**race.dict())
    db.add(db_race)
    db.commit()
    db.refresh(db_race)
    return db_race


def update_race(db: Session, race: schemas.RaceUpdate) -> schemas.Race:
    db_race = get_race(db=db, race_id=race.race_id)
    dict_to_attr(db_race, race.dict())
    db.commit()
    db.refresh(db_race)
    return db_race
