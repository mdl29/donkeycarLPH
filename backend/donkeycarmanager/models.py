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

    player = relationship("Player", lazy='subquery')


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
    max_duration = Column(Integer, nullable=False, default=5*60)  # Maximum race duration in ms

    player = relationship("Player", lazy='subquery')
    laptimers = relationship("LapTimer", backref="race", lazy='subquery')


class Worker(Base):
    __tablename__ = "worker"

    worker_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    type = Column(String(40), nullable=False)
    state = Column(String(40), nullable=False)


class Car(Base):
    __tablename__ = "car"

    name = Column(String, nullable=False, primary_key=True)
    ip = Column(String, nullable=False)
    color = Column(String, nullable=False)
    worker_id = Column(Integer, ForeignKey(Worker.worker_id), nullable=False)
    current_stage = Column(String, nullable=True)
    current_player_id = Column(Integer, ForeignKey(Player.player_id), nullable=True)
    current_race_id = Column(Integer, ForeignKey(Race.race_id), nullable=True)

    player = relationship("Player", lazy='subquery')
    race = relationship("Race", lazy='subquery')
    worker = relationship("Worker", lazy='subquery')


class LapTimer(Base):
    __tablename__ = "laptimer"

    laptimer_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    start_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )
    duration = Column(Integer, nullable=False)
    end_datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )
    race_id = Column(Integer, ForeignKey(Race.race_id), nullable=False)


class Job(Base):
    __tablename__ = "job"

    job_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey(Player.player_id), nullable=True)
    worker_id = Column(Integer, ForeignKey(Worker.worker_id), nullable=True)
    worker_type = Column(String(40), nullable=False)
    state = Column(String(40), nullable=False)
    name = Column(String(40), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow
    )
    rank = Column(Integer, nullable=False, unique=True, index=True)
    parameters = Column(String(800), nullable=True)

    fail_details = Column(String(1100), nullable=True)

    next_job_details = Column(String(2000), nullable=True)

    worker = relationship("Worker", backref="jobs", lazy='subquery')
    player = relationship("Player", lazy='subquery')
