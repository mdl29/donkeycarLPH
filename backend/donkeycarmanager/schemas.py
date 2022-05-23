from typing import Optional
from pydantic import BaseModel
import datetime


class PlayerBase(BaseModel):
    player_pseudo: str
    # See pydantic documentation here : https://pydantic-docs.helpmanual.io/usage/types/#datetime-types
    register_datetime: Optional[datetime.datetime]


class PlayerCreate(PlayerBase):
    pass


class Player(PlayerBase):
    player_id: int

    class Config:
        orm_mode = True


class DrivingWaitingQueueBase(BaseModel):
    player_id: int


class DrivingWaitingQueueCreate(DrivingWaitingQueueBase):
    pass


class DrivingWaitingQueue(DrivingWaitingQueueBase):
    rank: int
    start_waiting_datetime: datetime.datetime
    player: Player

    class Config:
        orm_mode = True
