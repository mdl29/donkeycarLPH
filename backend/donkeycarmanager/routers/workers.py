from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.workers as crud
from donkeycarmanager.dependencies import get_db

router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


@router.post("/", response_model=schemas.WorkerCreate)
def create_race(worker: schemas.WorkerCreate, db: Session = Depends(get_db)) -> schemas.Worker:
    return crud.create_worker(db=db, worker=worker)


@router.get("/", response_model=List[schemas.Worker])
def read_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[schemas.Worker]:
    return crud.get_workers(db, skip=skip, limit=limit)


@router.get("/{worker_id}", response_model=schemas.Worker)
def read_race(worker_id: int, db: Session = Depends(get_db)) -> schemas.Worker:
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return db_worker


@router.put("/{worker_id}", response_model=schemas.Worker)
def update_race(worker_id: int, worker: schemas.WorkerUpdate, db: Session = Depends(get_db)) -> schemas.Worker:
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return crud.update_worker(db, worker=worker)
