# All project global dependencies

import socketio

from donkeycarmanager.database import SessionLocal
from donkeycarmanager.helpers.socker_io_manager import SocketIOManager


def get_db():
    """
    Open the database session.
    :return: The SQL Alchemy database
    """
    db = SessionLocal()
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
