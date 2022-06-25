from typing import List, Union

import socketio
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect, WebSocket

from donkeycarmanager import schemas
import donkeycarmanager.crud.workers as crud
from donkeycarmanager.crud.workers_read import get_worker, get_workers
from donkeycarmanager.dependencies import get_db, get_job_scheduler, get_heartbeat_manager, get_sio
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
    return get_workers(db, skip=skip, limit=limit, worker_state=worker_state, worker_type=worker_type)


@router.get("/{worker_id}", response_model=schemas.Worker)
def read_worker(worker_id: int, db: Session = Depends(get_db)) -> schemas.Worker:
    db_worker = get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return db_worker


@router.put("/{worker_id}", response_model=schemas.Worker)
async def update_worker(worker_id: int, worker: schemas.WorkerUpdate,
                        db: Session = Depends(get_db),
                        sio: socketio.AsyncServer = Depends(get_sio),
                        job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Worker:
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Race not found")
    return await crud.update_worker(db, sio, job_sched=job_sched, worker=worker)


@router.post("/{worker_id}/clean",
             response_model=schemas.MassiveUpdateDeleteResult,
             description="Fail all running and paused jobs, could be used at worker startup")
async def clean_worker(worker_id: int,
                       fail_details: str = Body(
                           default=...,
                           embed=True,
                           description="Details that will be set on all job"),
                       db: Session = Depends(get_db))\
        -> schemas.MassiveUpdateDeleteResult:
    nb_affected_row = crud.clean_jobs(db=db, worker_id=worker_id, fail_details=fail_details)
    return schemas.MassiveUpdateDeleteResult(nb_affected_items=nb_affected_row)


@router.websocket("/workers/{worker_id}/wsHeartbeat")  # Set full path here as it doesn't work in route workers
async def websocket_endpoint(websocket: WebSocket, worker_id,
                             db: Session = Depends(get_db),
                             sio: socketio.AsyncServer = Depends(get_sio),
                             job_sched: AsyncJobScheduler = Depends(get_job_scheduler),
                             heartbeat_manager: WorkerHeartbeatManager = Depends(get_heartbeat_manager)):
    worker = crud.get_worker(db, worker_id=worker_id)
    await heartbeat_manager.connect(websocket, worker=worker, db=db, sio=sio, job_sched=job_sched)
    print(f"websocket_endpoint - Worker : {worker_id} connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await heartbeat_manager.disconnect(websocket, db=db, sio=sio, job_sched=job_sched)
        print(f"websocket_endpoint - Worker : {worker_id} disconnected")