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


class Race(Base):
    __tablename__ = "race"

    race_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey(Player.player_id), nullable=True)
    stage = Column(String, nullable=False)
    car_name = Column(String, nullable=False)  # Avoid circular reference don't use as FK
    start_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )

    player = relationship("Player")


class Car(Base):
    __tablename__ = "car"

    name = Column(String, nullable=False, primary_key=True)
    ip = Column(String, nullable=False)
    color = Column(String, nullable=False)
    current_stage = Column(String, nullable=True)
    current_player_id = Column(Integer, ForeignKey(Player.player_id), nullable=True)
    current_race_id = Column(Integer, ForeignKey(Race.race_id), nullable=True)

    player = relationship("Player")
    race = relationship("Race")


class LapTimer(Base):
    __tablename__ = "laptimer"

    laptimer_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    start_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )
    duration: Column(Integer, nullable=False)
    end_datetime: Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )
