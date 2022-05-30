import json
import socketio
from typing import Optional, List

from sqlalchemy import desc, asc, literal_column
from sqlalchemy.orm import Session

from donkeycarmanager import models, schemas
from donkeycarmanager.crud.players import get_player
from donkeycarmanager.schemas import EventDrivingWaitingQueueUpdated

RANKING_STEP = 1000  # How much place by default between 2 players.py in driving waiting queue


async def on_waiting_queue_change(db: Session, sio: socketio.AsyncServer) -> None:
    """
    Handle executed each time the player driving waiting queue changes.
    Sends an event to socket IO with the new list.
    :param db: Database.
    :param sio: Socket IO server.
    """
    # Send socket IO event with all queue elements
    db_queue = get_driving_waiting_queue_by_rank(db=db)
    schema_queue = EventDrivingWaitingQueueUpdated(drivePlayersWaitingPool=db_queue)
    await sio.emit('driveWaitingPool.updated',
                   json.loads(schema_queue.json()))  # Workaround to get pydantic deep conversation as dict


def get_driving_waiting_queue(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.DrivingWaitingQueue]:
    return db.query(models.DrivingWaitingQueue) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_driving_waiting_queue_by_rank(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.DrivingWaitingQueue]:
    return db.query(models.DrivingWaitingQueue)\
        .order_by(asc(models.DrivingWaitingQueue.rank))\
        .offset(skip)\
        .limit(limit)\
        .all()


async def create_driving_waiting_queue(db: Session, sio: socketio.AsyncServer,
                                       driving_waiting_queue: schemas.DrivingWaitingQueueCreate) \
        -> schemas.DrivingWaitingQueue:
    # Find ranking number
    last_driver: Optional[models.DrivingWaitingQueue] = db.query(models.DrivingWaitingQueue).\
        order_by(desc(models.DrivingWaitingQueue.rank)).limit(1).first()
    new_rank = last_driver.rank + RANKING_STEP if last_driver else RANKING_STEP  # Don't start at

    db_driving_waiting_queue = models.DrivingWaitingQueue(
        player_id=driving_waiting_queue.player_id,
        rank=new_rank)
    db.add(db_driving_waiting_queue)
    db.commit()
    await on_waiting_queue_change(db=db, sio=sio)  # Notify the queue was changed

    db.refresh(db_driving_waiting_queue)

    return db_driving_waiting_queue


def get_driving_queue_item(db: Session, player_id: int) -> schemas.DrivingWaitingQueue:
    return db.query(models.DrivingWaitingQueue) \
        .where(models.DrivingWaitingQueue.player_id == player_id).first()


async def move_player_after_another_in_waiting_queue(db: Session, sio: socketio.AsyncServer,
                                               to_move: models.DrivingWaitingQueue,
                                               before_item: models.DrivingWaitingQueue) -> schemas.DrivingWaitingQueue:
    """
    Move player waiting queue item (to_move) after another player waiting queue item.
    :param db: Database
    :param to_move: Player that will be moved.
    :param before_item: Reference player, will end before the player that should be moved.
    :return: Moved player.
    """
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
    await on_waiting_queue_change(db=db, sio=sio)  # Notify the queue was changed

    print(f'Moved {to_move.player.player_pseudo} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {before_item.player.player_pseudo} ({before_item.rank})')
    return to_move


async def move_player_before_another_in_waiting_queue(db: Session, sio: socketio.AsyncServer,
                                                to_move: models.DrivingWaitingQueue,
                                                after_item: models.DrivingWaitingQueue) -> schemas.DrivingWaitingQueue:
    """
    Move player waiting queue item (to_move) before another player waiting queue item.
    :param db: Database
    :param to_move: Player that will be moved.
    :param after_item: Reference player, will end after the player that should be moved.
    :return: The moved player.
    """
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
    await on_waiting_queue_change(db=db, sio=sio)  # Notify the queue was changed

    print(f'Moved {to_move.player.player_pseudo} from rank {old_rank} to rank {to_move.rank}'
          f'so that he is after {after_item.player.player_pseudo} ({after_item.rank})')
    return to_move


async def pop_player_in_queue(db: Session) -> Optional[models.DrivingWaitingQueue]:
    """
    Pop the first player queue item, meaning the item with the lowest rank.
    First in first out, it also ensure no one can pop the same item at the same time.
    Item will be removed from the queue.
    :param db: Database session.
    :return: The item or None if the queue is empty.
    """
    # See : https://stackoverflow.com/a/44760761
    first_player_stm = db.query(models.DrivingWaitingQueue.player_id).\
        order_by(asc(models.DrivingWaitingQueue.rank)).limit(1)
    delete_stm = models.DrivingWaitingQueue.__table__.delete(). \
        where(models.DrivingWaitingQueue.player_id.in_(first_player_stm)). \
        returning(literal_column('*'))

    result = db.execute(delete_stm).first()  # Not using ORM methods, as it's seems imposible to use returning with them
    db.commit()

    if result is None:
        return None

    player = get_player(db=db, player_id=result.player_id)  # Fix as the relation is populated

    return schemas.DrivingWaitingQueue(**result,
                                       player=player)
