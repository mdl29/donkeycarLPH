import logging
from fastapi import WebSocket
from sqlalchemy.orm import Session

import socketio

from donkeycarmanager import models
from donkeycarmanager.crud.jobs_read import get_jobs
from donkeycarmanager.emitters.workers import on_worker_update
from donkeycarmanager.schemas import WorkerState, JobState
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler


class WorkerHeartbeatManager:
    def __init__(self, db: Session):
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        # Ensure every worker is stopped, before handling heartbeat
        db.query(models.Worker).update({models.Worker.state: WorkerState.STOPPED})
        db.commit()
        self.logger.debug('All workers set to STOPPED')

    async def connect(self, websocket: WebSocket, worker: models.Worker,
                      db: Session,
                      sio: socketio.AsyncServer,
                      job_sched: AsyncJobScheduler):
        websocket.donkeycar_worker = worker  # Ugly but didn't find better
        await websocket.accept()
        db.refresh(worker)  # Ensure we have an up to date version of worker

        # Check if the worker as already something to be busy with
        running_jobs = get_jobs(db, limit=1, by_rank=True,
                                no_worker=True, worker_id=worker.worker_id,
                                job_states=[
                                    JobState.RUNNING, JobState.PAUSING, JobState.PAUSED,
                                    JobState.CANCELLING])
        if len(running_jobs) > 0:
            worker.state = WorkerState.BUSY
        else:
            worker.state = WorkerState.AVAILABLE

        db.commit()
        self.logger.info(f"Worker connected id:%i, state:%s", worker.worker_id, worker.state)

        await job_sched.on_worker_changed(worker)
        await on_worker_update(sio, worker)

    async def disconnect(self, websocket: WebSocket,
                         db: Session,
                         sio: socketio.AsyncServer,
                         job_sched: AsyncJobScheduler):
        """
        Called when websocket is disconnected.
        """
        worker: models.Worker = websocket.donkeycar_worker
        db.refresh(worker)  # Ensure we have an up to date version of worker
        worker.state = WorkerState.STOPPED

        # Here comes what I call a magical "NON IDENTIFIED" bug
        # Sometimes (no idea why), db.commit() doesn't update the worker state here
        db.query(models.Worker).filter(models.Worker.worker_id == worker.worker_id).update({models.Worker.state: WorkerState.STOPPED})

        db.commit()
        self.logger.info(f"Worker disconnected : {worker.worker_id}")
        await job_sched.on_worker_changed(worker)
        await on_worker_update(sio, worker)
