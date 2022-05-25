from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.cars as crud
from donkeycarmanager.dependencies import get_db

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)


@router.post("/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = crud.get_car(db, name=car.name)
    if db_car:
        raise HTTPException(status_code=400, detail="Car already registered")
    return crud.create_car(db=db, car=car)


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
def update_car(car_name: str, car: schemas.CarUpdate, db: Session = Depends(get_db)) -> schemas.Car:
    db_car = crud.get_car(db, name=car_name)
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return crud.update_car(db, car=car)
