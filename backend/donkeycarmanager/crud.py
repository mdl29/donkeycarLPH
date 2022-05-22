from typing import Optional
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas


def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.player_id == player_id).first()


def get_player_by_pseudo(db: Session, player_pseudo: str):
    return db.query(models.Player).filter(models.Player.player_pseudo == player_pseudo).first()


def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()


def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(
        player_pseudo=player.player_pseudo,
        register_datetime=player.register_datetime)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def get_driving_waiting_queue(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DrivingWaitingQueue) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_driving_waiting_queue_by_rank(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DrivingWaitingQueue)\
        .order_by(asc(models.DrivingWaitingQueue.rank))\
        .offset(skip)\
        .limit(limit)\
        .all()


def create_driving_waiting_queue(db: Session, driving_waiting_queue: schemas.DrivingWaitingQueueCreate):
    # Find ranking number
    last_driver: Optional[models.DrivingWaitingQueue] = db.query(models.DrivingWaitingQueue).\
        order_by(desc(models.DrivingWaitingQueue.rank)).limit(1).first()
    new_rank = last_driver.rank + 1000 if last_driver else 1

    db_driving_waiting_queue = models.DrivingWaitingQueue(
        player_id=driving_waiting_queue.player_id,
        rank=new_rank)
    db.add(db_driving_waiting_queue)
    db.commit()
    db.refresh(db_driving_waiting_queue)
    return db_driving_waiting_queue
