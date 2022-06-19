# All project global dependencies

import socketio
from fastapi import Depends

from donkeycarmanager.database import SessionLocal
from donkeycarmanager.helpers.socker_io_manager import SocketIOManager
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler
from donkeycarmanager.worker_heartbeat_manager import WorkerHeartbeatManager

db = SessionLocal()

def get_db():
    """
    Open the database session.
    :return: The SQL Alchemy database
    """
    try:
        yield db
    finally:
        db.close()


sm = SocketIOManager(cors_allowed_origins=[])  # See issue : https://github.com/pyropy/fastapi-socketio/issues/13


def get_sio() -> socketio.AsyncServer:
    """
    Returns socket IO instance.
    :return:
    """
    return sm.getSocketIO()


job_scheduler = AsyncJobScheduler(db, get_sio())


def get_job_scheduler() -> AsyncJobScheduler:
    """
    Returns the job_scheduler singleton
    :param db: Database, injected
    :param sio: SocketIO, injected
    :return:
    """
    return job_scheduler


def get_heartbeat_manager(db: SessionLocal = Depends(get_db)) -> WorkerHeartbeatManager:
    """
    Returns heartbeat manager.
    :param db: Database, injected
    :return: The hearbeat manager.
    """
    heartbeat_manager = WorkerHeartbeatManager(db=db)
    yield heartbeat_manager
