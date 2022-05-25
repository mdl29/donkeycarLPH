from typing import List

from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr


def get_car(db: Session, name: str) -> schemas.Car:
    return db.query(models.Car).filter(models.Car.name == name).first()


def get_cars(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Car]:
    return db.query(models.Car).offset(skip).limit(limit).all()


def create_car(db: Session, car: schemas.CarCreate) -> schemas.Car:
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def update_car(db: Session, car: schemas.CarUpdate) -> schemas.Car:
    db_car = get_car(db=db, name=car.name)
    dict_to_attr(db_car, car.dict())
    db.commit()
    db.refresh(db_car)
    return db_car
