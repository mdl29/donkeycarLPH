from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.races as crud
from donkeycarmanager.dependencies import get_db

router = APIRouter(
    prefix="/races",
    tags=["Races"]
)


@router.post("/", response_model=schemas.Race)
def create_race(race: schemas.RaceCreate, db: Session = Depends(get_db)) -> schemas.Race:
    return crud.create_race(db=db, race=race)


@router.get("/", response_model=List[schemas.Race])
def read_races(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.Race]:
    return crud.get_races(db, skip=skip, limit=limit)


@router.get("/{race_id}", response_model=schemas.Race)
def read_race(race_id: int, db: Session = Depends(get_db)):
    db_race = crud.get_race(db, race_id=race_id)
    if db_race is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return db_race


@router.put("/{race_id}", response_model=schemas.Race)
def update_race(race_id: int, race: schemas.RaceUpdate, db: Session = Depends(get_db)) -> schemas.Race:
    db_race = crud.get_race(db, race_id=race_id)
    if db_race is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return crud.update_race(db, race=race)
