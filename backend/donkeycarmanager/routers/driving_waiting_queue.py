from typing import List

import socketio
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.driving_waiting_queue as crud
from donkeycarmanager.dependencies import get_db, get_sio

router = APIRouter(
    prefix="/drivingWaitingQueue",
    tags=["DriveWaitingQueue"]
)


@router.post("/", response_model=schemas.DrivingWaitingQueue)
async def create_player_in_driving_queue(driving_waiting_queue: schemas.DrivingWaitingQueueCreate,
                                         db: Session = Depends(get_db), sio: socketio.AsyncServer = Depends(get_sio)):
    # TODO check player_id isn't already in the waiting queue
    return await crud.create_driving_waiting_queue(db=db, sio=sio, driving_waiting_queue=driving_waiting_queue)


@router.get("/", response_model=List[schemas.DrivingWaitingQueue])
def read_players_in_driving_queue(by_rank: bool = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if by_rank:
        waiting_players = crud.get_driving_waiting_queue_by_rank(db, skip=skip, limit=limit)
    else:
        waiting_players = crud.get_driving_waiting_queue(db, skip=skip, limit=limit)
    return waiting_players


@router.post("/{player_id}/move_after",
             description="Move Player (player_id) after player with after_player_id",
             response_model=schemas.DrivingWaitingQueue)
async def move_player_in_driving_queue(
        player_id: int,
        after_player_id: int = Body(
            default=...,
            embed=True,
            description="Let's take Toto and toto.player_id == player_id (path parameter),"
                        "and Titi with titi.player_id == after_player_id. After this request "
                        "Toto will be just after Titi in the waiting queue. Meaning that Titi "
                        "will start before Toto."
        ),
        db: Session = Depends(get_db),
        sio: socketio.AsyncServer = Depends(get_sio)):
    to_move = crud.get_driving_queue_item(db, player_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player to be moved with id {player_id} "
                                                    f"not found in driving waiting queue")
    before_item = crud.get_driving_queue_item(db, after_player_id)
    if before_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player with id {after_player_id}, to be after "
                                                    f"not found in driving waiting queue")

    return await crud.move_player_after_another_in_waiting_queue(
        db=db, sio=sio, to_move=to_move, before_item=before_item)


@router.post("/{player_id}/move_before",
             description="Move Player (player_id) before player with before_player_id",
             response_model=schemas.DrivingWaitingQueue)
async def move_player_in_driving_queue(
        player_id: int,
        before_player_id: int = Body(
            default=...,
            embed=True,
            description="Let's take Toto and toto.player_id == player_id (path parameter),"
                        "and Titi with titi.player_id == before_player_id. After this request "
                        "Toto will be just before Titi in the waiting queue. Meaning that Toto"
                        " will start before Titi."
        ),
        db: Session = Depends(get_db),
        sio: socketio.AsyncServer = Depends(get_sio)):
    to_move = crud.get_driving_queue_item(db, player_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player to be moved with id {player_id} "
                                                    f"not found in driving waiting queue")
    after_item = crud.get_driving_queue_item(db, before_player_id)
    if after_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player with id {before_player_id}, to be before "
                                                    f"not found in driving waiting queue")

    return await crud.move_player_before_another_in_waiting_queue(
        db=db, sio=sio, to_move=to_move, after_item=after_item)
