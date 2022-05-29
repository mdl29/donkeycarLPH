import json
from typing import NoReturn

import socketio

from donkeycarmanager.schemas import LapTimer, EventLapTimerAdded


async def on_laptimer_added(sio: socketio.AsyncServer, laptimer: LapTimer) -> NoReturn:
    """
    Handler executed each time a car is added.
    :param sio: Socket IO server.
    :param laptimer: The laptimer that was added.
    """
    payload = EventLapTimerAdded(laptimer=laptimer)
    await sio.emit('car.added',
                   json.loads(payload.json()))  # Workaround to get pydantic deep convertion as dict
