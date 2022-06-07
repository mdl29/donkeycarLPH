from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect, WebSocket

from donkeycarmanager import schemas
import donkeycarmanager.crud.workers as crud
from donkeycarmanager.dependencies import get_db
from donkeycarmanager.worker_heartbeat_manager import WorkerHeartbeatManager

router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


@router.post("/", response_model=schemas.Worker)
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


heartbeat_manager = WorkerHeartbeatManager()


@router.websocket("/workers/{worker_id}/wsHeartbeat")  # Set full path here as it doesn't work in route workers
async def websocket_endpoint(websocket: WebSocket, worker_id, db=Depends(get_db)):
    worker = crud.get_worker(db, worker_id=worker_id)
    await heartbeat_manager.connect(websocket, worker=worker, db=db)
    print(f"websocket_endpoint - Worker : {worker_id} connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        heartbeat_manager.disconnect(websocket)
        print(f"websocket_endpoint - Worker : {worker_id} disconnected")