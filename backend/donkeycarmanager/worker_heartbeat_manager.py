from typing import Mapping, Dict

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from donkeycarmanager import models
from donkeycarmanager.dependencies import get_db
from donkeycarmanager.schemas import Worker, WorkerState


class WorkerHeartbeatManager:
    def __init__(self):
        # self.active_connections: Dict[int, WebSocket] = {}  # Map worker_id to their websocket
        self.db = None

    async def connect(self, websocket: WebSocket, worker: models.Worker, db: Session):
        self.db = db  # Ugly didn't find better to handle injection
        websocket.donkeycar_worker = worker  # Ugly but didn't find better
        await websocket.accept()
        worker.state = WorkerState.AVAILABLE
        self.db.commit()
        print(f"Worker connected : {worker.worker_id}")
        # self.active_connections[worker.worker_id] = websocket

    def disconnect(self, websocket: WebSocket):
        """
        Called when websocket is disconnected.
        :param websocket:
        :param worker:
        :return:
        """
        worker: models.Worker = websocket.donkeycar_worker
        worker.state = WorkerState.STOPPED
        self.db.commit()
        print(f"Worker disconnected : {worker.worker_id}")
        # self.active_connections.pop(worker.worker_id)
