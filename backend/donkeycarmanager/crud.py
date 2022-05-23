from typing import Optional
from sqlalchemy import asc, desc
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.database import engine

RANKING_STEP = 1000  # How much place by default between 2 players in driving waiting queue

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
    new_rank = last_driver.rank + RANKING_STEP if last_driver else RANKING_STEP  # Don't start at

    db_driving_waiting_queue = models.DrivingWaitingQueue(
        player_id=driving_waiting_queue.player_id,
        rank=new_rank)
    db.add(db_driving_waiting_queue)
    db.commit()
    db.refresh(db_driving_waiting_queue)
    return db_driving_waiting_queue


def get_driving_queue_item(db: Session, player_id: int):
    return db.query(models.DrivingWaitingQueue) \
        .where(models.DrivingWaitingQueue.player_id == player_id).first()


"""
    Will move player "to_move.player" so that it is after "before_item.player".
"""
def move_player_after_an_other_in_waiting_queue(db: Session, to_move: models.DrivingWaitingQueue,
                                                before_item: models.DrivingWaitingQueue):
    old_rank = to_move.rank

    # Find the first queued element after the player, the one that is the next after him
    existing_player_after = db.query(models.DrivingWaitingQueue).filter(models.DrivingWaitingQueue.rank > before_item.rank)\
        .order_by(asc(models.DrivingWaitingQueue.rank))\
        .limit(1).first()

    if existing_player_after:
        if existing_player_after.player_id == to_move.player_id:  # No need to move it, it's already after
            return to_move

        delta = existing_player_after.rank - before_item.rank
        if delta > 0:
            to_move.rank = before_item.rank + delta // 2
        else:
            raise ValueError('Impossible to rank this player no values left')
    else:  # No one after the referenced player, simply putting our player here with the RANKING_STEP
        to_move.rank = before_item.rank + RANKING_STEP

    db.commit()
    print(f'Moved {to_move.player.player_pseudo} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {before_item.player.player_pseudo} ({before_item.rank})')
    return to_move


"""
    Will move player "to_move.player" so that it is before "after_item.player".
"""
def move_player_before_an_other_in_waiting_queue(db: Session, to_move: models.DrivingWaitingQueue,
                                                after_item: models.DrivingWaitingQueue):
    old_rank = to_move.rank

    # Find the first queued element after the player, the one that is the next after him
    existing_player_before = db.query(models.DrivingWaitingQueue).filter(
        models.DrivingWaitingQueue.rank < after_item.rank) \
        .order_by(desc(models.DrivingWaitingQueue.rank)) \
        .limit(1).first()

    if existing_player_before:
        if existing_player_before.player_id == to_move.player_id:  # No need to move it, it's already after
            return to_move

        delta = after_item.rank - existing_player_before.rank
        if delta > 0:
            to_move.rank = after_item.rank - delta // 2
        else:
            raise ValueError('Impossible to rank this player no values left')
    else:  # No one after the referenced player, simply putting our player here with the RANKING_STEP
        to_move.rank = after_item.rank // 2  # Let some place behind it and before it

    db.commit()
    print(f'Moved {to_move.player.player_pseudo} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {after_item.player.player_pseudo} ({after_item.rank})')
    return to_move
