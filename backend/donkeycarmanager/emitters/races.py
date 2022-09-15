import json
from typing import NoReturn

import socketio

from donkeycarmanager.schemas import Race, EventRaceUpdated


async def on_race_updated(sio: socketio.AsyncServer, race: Race) -> NoReturn:
    """
    Handler executed each time a car is added.
    :param sio: Socket IO server.
    :param race: The updated race.
    """
    payload = EventRaceUpdated(race=race)
    json_payload = json.loads(payload.json())  # Workaround to get pydantic deep convertion as dict
    await sio.emit('race.all.updated', json_payload)
    await sio.emit(f'race.{race.race_id}.updated', json_payload)
