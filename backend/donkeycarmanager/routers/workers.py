from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect, WebSocket

from donkeycarmanager import schemas
import donkeycarmanager.crud.workers as crud
from donkeycarmanager.dependencies import get_db, get_job_scheduler, db
from donkeycarmanager.schemas import WorkerState, WorkerType
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler
from donkeycarmanager.worker_heartbeat_manager import WorkerHeartbeatManager

router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


@router.post("/", response_model=schemas.Worker)
def create_worker(worker: schemas.WorkerCreate, db: Session = Depends(get_db)) -> schemas.Worker:
    return crud.create_worker(db=db, worker=worker)


@router.get("/", response_model=List[schemas.Worker])
def read_workers(skip: int = 0, limit: int = 100,
                 worker_state: Union[None, WorkerState] = None,
                 worker_type: Union[None, WorkerType] = None,
                 db: Session = Depends(get_db)) -> List[schemas.Worker]:
    return crud.get_workers(db, skip=skip, limit=limit, worker_state=worker_state, worker_type=worker_type)


@router.get("/{worker_id}", response_model=schemas.Worker)
def read_worker(worker_id: int, db: Session = Depends(get_db)) -> schemas.Worker:
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return db_worker


@router.put("/{worker_id}", response_model=schemas.Worker)
async def update_worker(worker_id: int, worker: schemas.WorkerUpdate,
                db: Session = Depends(get_db), job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Worker:
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return await crud.update_worker(db, job_sched=job_sched, worker=worker)


heartbeat_manager = WorkerHeartbeatManager(db=db)


@router.websocket("/workers/{worker_id}/wsHeartbeat")  # Set full path here as it doesn't work in route workers
async def websocket_endpoint(websocket: WebSocket, worker_id, db=Depends(get_db), job_sched=Depends(get_job_scheduler)):
    worker = crud.get_worker(db, worker_id=worker_id)
    await heartbeat_manager.connect(websocket, worker=worker, db=db, job_sched=job_sched)
    print(f"websocket_endpoint - Worker : {worker_id} connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await heartbeat_manager.disconnect(websocket, db=db, job_sched=job_sched)
        print(f"websocket_endpoint - Worker : {worker_id} disconnected")