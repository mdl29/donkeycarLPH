from typing import List, NoReturn
import socketio
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.helpers.utils import dict_to_attr
import donkeycarmanager.emitters.cars as emitters


def get_car(db: Session, name: str) -> schemas.Car:
    return db.query(models.Car).filter(models.Car.name == name).first()


def get_cars(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Car]:
    return db.query(models.Car).offset(skip).limit(limit).all()


async def create_car(db: Session, sio: socketio.AsyncServer, car: schemas.CarCreate) -> schemas.Car:
    db_car = models.Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)

    await emitters.on_car_added(sio=sio, car=db_car)

    return db_car


async def update_car(db: Session, sio: socketio.AsyncServer, car: schemas.CarUpdate) -> schemas.Car:
    db_car = get_car(db=db, name=car.name)
    dict_to_attr(db_car, car.dict())
    db.commit()
    db.refresh(db_car)

    await emitters.on_car_updated(sio=sio, car=db_car)

    return db_car


async def delete_car(db: Session, sio: socketio.AsyncServer, car_name: str) -> NoReturn:
    db_car = get_car(db=db, name=car_name)
    db.delete(db_car)
    db.commit()

    await emitters.on_car_removed(sio=sio, car_name=car_name)
