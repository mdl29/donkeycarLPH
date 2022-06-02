from typing import List, Union
import socketio
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.cars as crud
from donkeycarmanager.dependencies import get_db, get_sio

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)


@router.post("/", response_model=schemas.Car)
async def create_car(car: schemas.CarCreate, db: Session = Depends(get_db),
                     sio: socketio.AsyncServer = Depends(get_sio)):
    db_car = crud.get_car(db, name=car.name)
    if db_car:
        raise HTTPException(status_code=400, detail="Car already registered")
    return await crud.create_car(db=db, sio=sio, car=car)


@router.get("/", response_model=List[schemas.Car])
def read_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_cars(db, skip=skip, limit=limit)


@router.get("/{car_name}", response_model=schemas.Car)
def read_car(car_name: str, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, name=car_name)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_car


@router.put("/{car_name}", response_model=schemas.Car)
async def update_car(car_name: str, car: schemas.CarUpdate, db: Session = Depends(get_db),
                     sio: socketio.AsyncServer = Depends(get_sio)) -> schemas.Car:
    db_car = crud.get_car(db, name=car_name)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return await crud.update_car(db=db, sio=sio, car=car)


@router.delete("/{car_name}")
async def delete_car(car_name: str, db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio)):
    db_car = crud.get_car(db, name=car_name)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return await crud.delete_car(db=db, sio=sio, car_name=db_car.name)
