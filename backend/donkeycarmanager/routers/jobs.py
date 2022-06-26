from typing import List, Optional, Union

import socketio
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.jobs as crud
import donkeycarmanager.crud.jobs_read as crudRead
from donkeycarmanager.dependencies import get_db, get_sio, get_job_scheduler
from donkeycarmanager.schemas import JobState, WorkerType
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.post("/", response_model=schemas.Job)
async def create_job(job: schemas.JobCreate,
                     db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio),
                     job_sched: AsyncJobScheduler = Depends(get_job_scheduler)):
    # TODO check job_id isn't already in the waiting queue
    return await crud.create_job(db=db, sio=sio, job_sched=job_sched, job=job)


@router.get("/{job_id}", response_model=schemas.Job)
def get_job( job_id: int, db: Session = Depends(get_db)) -> schemas.Job:
    db_job = crudRead.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.get("/", response_model=List[schemas.Job])
def read_jobs(by_rank: bool = True, skip: int = 0, limit: int = 100,
              worker_id: Union[None, int] = None,
              no_worker: Union[None, bool] = None,
              worker_type: Union[None, WorkerType] = None,
              job_states: Union[None, List[JobState]] = Query(default=None,
                                                             description="If multiple state, will use OR operator"),
              db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio)) -> List[schemas.Job]:
    return crudRead.get_jobs(db, skip=skip, by_rank=by_rank,
                         worker_id=worker_id, no_worker=no_worker, worker_type=worker_type,
                         job_states=job_states, limit=limit)


@router.post("/{job_id}/move_after",
             description="Move Job (with job_id) after job with after_job_id",
             response_model=schemas.Job)
async def move_job_after(
        job_id: int,
        after_job_id: int = Body(
            default=...,
            embed=True,
            description="Let's take jobA with job_id (path parameter),"
                        "and jobB with after_job_id. After this request "
                        " will be just after jobB in the job list. Meaning that jobB "
                        "will start before jobA."
        ),
        db: Session = Depends(get_db),
        sio: socketio.AsyncServer = Depends(get_sio)) -> schemas.Job:
    to_move = crudRead.get_job(db, job_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Job to be moved with id {job_id} "
                                                    f"not found in jobs queue")
    before_item = crudRead.get_job(db, after_job_id)
    if before_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Job with id {after_job_id}, to be after "
                                                    f"not found in jobs queue")

    return await crud.move_job_after_another_in_queue(
        db=db, sio=sio, to_move=to_move, before_item=before_item)


@router.post("/{job_id}/move_before",
             description="Move Job (job_id) before player with before_job_id",
             response_model=schemas.Job)
async def move_job_before(
        job_id: int,
        before_job_id: int = Body(
            default=...,
            embed=True,
            description="Let's take jobA with job_id (path parameter),"
                        "and jobB with before_job_id. After this request "
                        "jobA will be just before jobB in the job list. Meaning that jobA"
                        " will start before jobB."
        ),
        db: Session = Depends(get_db),
        sio: socketio.AsyncServer = Depends(get_sio)) -> schemas.Job:
    to_move = crudRead.get_job(db, job_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Job to be moved with id {job_id} "
                                                    f"not found in jobs queue")
    after_item = crudRead.get_job(db, before_job_id)
    if after_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Job with id {before_job_id}, to be before "
                                                    f"not found in jobs queue")

    return await crud.move_job_before_another_queue(
        db=db, sio=sio, to_move=to_move, after_item=after_item)


@router.put("/{job_id}", response_model=schemas.Job)
async def update_job(job: schemas.JobUpdate,
                     job_id: int,
                     db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio),
                     job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Job:
    db_job = crudRead.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return await crud.update_job(db, sio=sio, job_sched=job_sched, job=job)


async def check_and_update_job_state(job_id: int, job_state: JobState,
                     db: Session, sio: socketio.AsyncServer,
                     job_sched: AsyncJobScheduler) -> schemas.Job:
    db_job = crudRead.get_job(db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return await crud.update_job_state(db, sio, job_sched, job_id, job_state)


@router.post("/{job_id}/pause", response_model=schemas.Job)
async def update_job_resuming(job_id: int,
                            db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio),
                            job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Job:
    return await check_and_update_job_state(job_id, JobState.PAUSING, db, sio, job_sched)


@router.post("/{job_id}/resume", response_model=schemas.Job)
async def update_job_resuming(job_id: int,
                            db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio),
                            job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Job:
    return await check_and_update_job_state(job_id, JobState.RESUMING, db, sio, job_sched)


@router.post("/{job_id}/cancel", response_model=schemas.Job)
async def update_job_cancelling(job_id: int,
                            db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio),
                            job_sched: AsyncJobScheduler = Depends(get_job_scheduler)) -> schemas.Job:
    return await check_and_update_job_state(job_id, JobState.CANCELLING, db, sio, job_sched)