import json
from typing import NoReturn

import socketio

from donkeycarmanager.schemas import Car, EventCarRemoved, EventCarUpdated, EventCarAdded


async def on_car_added(sio: socketio.AsyncServer, car: Car) -> NoReturn:
    """
    Handler executed each time a car is added.
    :param sio: Socket IO server.
    :param car: Car that was added.
    """
    payload = EventCarAdded(car=car)
    await sio.emit('car.added',
                   json.loads(payload.json()))  # Workaround to get pydantic deep convertion as dict


async def on_car_updated(sio: socketio.AsyncServer, car: Car) -> NoReturn:
    """
    Handler executed each time a car is updated.
    :param sio: Socket IO server.
    :param car: Car that was added.
    """
    payload = EventCarUpdated(car=car)
    await sio.emit('car.updated',
                   json.loads(payload.json()))  # Workaround to get pydantic deep convertion as dict


async def on_car_removed(sio: socketio.AsyncServer, car_name: str) -> NoReturn:
    """
    Handler executed each time a car is deleted from database.
    :param sio: Socket IO server.
    :param car_name: Name of the deleted car.
    """
    payload = EventCarRemoved(car_name=car_name)
    await sio.emit('car.removed',
                   json.loads(payload.json()))  # Workaround to get pydantic deep convertion as dict
