from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime, pytz

from donkeycarmanager.database import Base


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    player_pseudo = Column(String, unique=True)
    register_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow)


class DrivingWaitingQueue(Base):
    __tablename__ = "driving_waiting_queue"

    player_id = Column(Integer, ForeignKey(Player.player_id), primary_key=True)
    rank = Column(Integer, nullable=False, unique=True, index=True)
    start_waiting_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )

    player = relationship("Player")
