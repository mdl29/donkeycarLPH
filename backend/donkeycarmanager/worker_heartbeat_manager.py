import logging
from fastapi import WebSocket
from sqlalchemy.orm import Session

from donkeycarmanager import models
from donkeycarmanager.schemas import WorkerState
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler


class WorkerHeartbeatManager:
    def __init__(self):
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    def defered_init_after_db_created(self, db: Session):
        """
        Run after db is inited
        """

        # Ensure every worker is stopped, before handling heartbeat
        db.query(models.Worker).update({models.Worker.state: WorkerState.STOPPED})
        db.commit()
        self.logger.debug('All workers set to STOPPED')

    async def connect(self, websocket: WebSocket, worker: models.Worker, db: Session, job_sched: AsyncJobScheduler):
        websocket.donkeycar_worker = worker  # Ugly but didn't find better
        await websocket.accept()
        worker.state = WorkerState.AVAILABLE
        db.commit()
        self.logger.info(f"Worker connected : {worker.worker_id}")
        await job_sched.on_worker_changed(worker)

    async def disconnect(self, websocket: WebSocket, db: Session, job_sched: AsyncJobScheduler):
        """
        Called when websocket is disconnected.
        :param websocket:
        :param worker:
        :return:
        """
        worker: models.Worker = websocket.donkeycar_worker
        worker.state = WorkerState.STOPPED

        # Here comes what I call a magical "NON IDENTIFIED" bug
        # Sometimes (no idea why), db.commit() doesn't update the worker state here
        db.query(models.Worker).filter(models.Worker.worker_id == worker.worker_id).update({models.Worker.state: WorkerState.STOPPED})

        db.commit()
        self.logger.info(f"Worker disconnected : {worker.worker_id}")
        await job_sched.on_worker_changed(worker)
