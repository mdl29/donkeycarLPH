from fastapi import WebSocket
from sqlalchemy.orm import Session

from donkeycarmanager import models
from donkeycarmanager.schemas import WorkerState
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler


class WorkerHeartbeatManager:
    def __init__(self):
        pass

    async def connect(self, websocket: WebSocket, worker: models.Worker, db: Session, job_sched: AsyncJobScheduler):
        websocket.donkeycar_worker = worker  # Ugly but didn't find better
        await websocket.accept()
        worker.state = WorkerState.AVAILABLE
        db.commit()
        print(f"Worker connected : {worker.worker_id}")
        job_sched.on_worker_changed(worker)

    def disconnect(self, websocket: WebSocket, db: Session, job_sched: AsyncJobScheduler):
        """
        Called when websocket is disconnected.
        :param websocket:
        :param worker:
        :return:
        """
        worker: models.Worker = websocket.donkeycar_worker
        worker.state = WorkerState.STOPPED
        db.commit()
        print(f"Worker disconnected : {worker.worker_id}")
        job_sched.on_worker_changed(worker)
