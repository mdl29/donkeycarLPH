# All project global dependencies

import socketio

from donkeycarmanager.database import SessionLocal
from donkeycarmanager.helpers.socker_io_manager import SocketIOManager
from donkeycarmanager.services.async_job_scheduler import AsyncJobScheduler

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
# Is started as FastAPI start, where we have access to the asyncIO loop used by fastAPI


def get_job_scheduler() -> AsyncJobScheduler:
    """
    Returns the job_scheduler singleton
    :return:
    """
    return job_scheduler
