from typing import List, Union
import socketio

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.laptimers as crud
from donkeycarmanager.dependencies import get_db, get_sio

router = APIRouter(
    prefix="/laptimers",
    tags=["Laptimers"]
)


@router.post("/", response_model=schemas.LapTimer)
async def create_laptimer(laptimer: schemas.LapTimerCreate, db: Session = Depends(get_db),
                          sio: socketio.AsyncServer = Depends(get_sio)) -> schemas.LapTimer:
    return await crud.create_laptimer(db=db, sio=sio, laptimer=laptimer)


@router.get("/", response_model=List[schemas.LapTimer])
def read_laptimers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.LapTimer]:
    return crud.get_laptimers(db, skip=skip, limit=limit)


@router.get("/{laptimer_id}", response_model=schemas.LapTimer)
def read_laptimer(laptimer_id: int, db: Session = Depends(get_db)):
    db_laptimer = crud.get_laptimer(db, laptimer_id=laptimer_id)
    if db_laptimer is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return db_laptimer


@router.put("/{laptimer_id}", response_model=schemas.LapTimer)
def update_laptimer(laptimer_id: int, laptimer: schemas.LapTimerUpdate, db: Session = Depends(get_db)) -> schemas.LapTimer:
    db_laptimer = crud.get_laptimer(db, laptimer_id=laptimer_id)
    if db_laptimer is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return crud.update_laptimer(db, laptimer=laptimer)
