from typing import NoReturn

import socketio
import json

from donkeycarmanager.schemas import Worker, EventWorkerChanged


async def on_worker_update(sio: socketio.AsyncServer, worker: Worker) -> NoReturn:
    """
    Handler executed each time a car is added.
    :param sio: Socket IO server.
    :param worker: Worker that was added.
    """
    payload = EventWorkerChanged(worker=worker)
    await sio.emit('worker.all.updated',
                   json.loads(payload.json()))  # Workaround to get pydantic deep convertion as dict
