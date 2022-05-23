from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from donkeycarmanager import crud, models, schemas
from donkeycarmanager.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/players/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_pseudo(db, player_pseudo=player.player_pseudo)
    if db_player:
        raise HTTPException(status_code=400, detail="Pseudo already registered")
    return crud.create_player(db=db, player=player)


@app.get("/players/", response_model=List[schemas.Player])
def read_players(player_pseudo: Union[str, None] = Query(
        default=None,
        description="Will get a list a player matching this pseudo, as pseudo are unique "
                    "it should at most return one player."
    ),
        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    if player_pseudo:
        return [crud.get_player_by_pseudo(db, player_pseudo=player_pseudo)]

    return crud.get_players(db, skip=skip, limit=limit)


@app.get("/player/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@app.post("/drivingWaitingQueue/", response_model=schemas.DrivingWaitingQueue)
def create_player_in_driving_queue(driving_waiting_queue: schemas.DrivingWaitingQueueCreate, db: Session = Depends(get_db)):
    # TODO check player_id isn't already in the waiting queue
    return crud.create_driving_waiting_queue(db=db, driving_waiting_queue=driving_waiting_queue)


@app.get("/drivingWaitingQueue/", response_model=List[schemas.DrivingWaitingQueue])
def read_players_in_driving_queue(by_rank: bool = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if by_rank:
        waiting_players = crud.get_driving_waiting_queue_by_rank(db, skip=skip, limit=limit)
    else:
        waiting_players = crud.get_driving_waiting_queue(db, skip=skip, limit=limit)
    return waiting_players


@app.post("/drivingWaitingQueue/{player_id}/move_after", response_model=schemas.DrivingWaitingQueue,
          description="Move Player (player_id) after player with after_player_id")
def move_player_in_driving_queue(player_id: int,
                                 after_player_id: int = Body(
                                     default=...,
                                     embed=True,
                                     description="Let's take Toto and toto.player_id == player_id (path parameter),"
                                                 "and Titi with titi.player_id == after_player_id. After this request "
                                                 "Toto will be just after Titi in the waiting queue. Meaning that Titi "
                                                 "will start before Toto."
                                 ),
                                 db: Session = Depends(get_db)):
    to_move = crud.get_driving_queue_item(db, player_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player to be moved with id {player_id} "
                                                    f"not found in driving waiting queue")
    before_item = crud.get_driving_queue_item(db, after_player_id)
    if before_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player with id {after_player_id}, to be after "
                                                    f"not found in driving waiting queue")

    return crud.move_player_after_an_other_in_waiting_queue(db, to_move, before_item)


@app.post("/drivingWaitingQueue/{player_id}/move_before", response_model=schemas.DrivingWaitingQueue,
          description="Move Player (player_id) before player with before_player_id")
def move_player_in_driving_queue(player_id: int,
                                 before_player_id: int = Body(
                                     default=...,
                                     embed=True,
                                     description="Let's take Toto and toto.player_id == player_id (path parameter),"
                                                 "and Titi with titi.player_id == before_player_id. After this request "
                                                 "Toto will be just before Titi in the waiting queue. Meaning that Toto"
                                                 " will start before Titi."
                                 ),
                                 db: Session = Depends(get_db)):
    to_move = crud.get_driving_queue_item(db, player_id)
    if to_move is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player to be moved with id {player_id} "
                                                    f"not found in driving waiting queue")
    after_item = crud.get_driving_queue_item(db, before_player_id)
    if after_item is None:  # Guard ensure the player we want to move exists
        raise HTTPException(status_code=404, detail=f"Player with id {before_player_id}, to be before "
                                                    f"not found in driving waiting queue")

    return crud.move_player_before_an_other_in_waiting_queue(db, to_move, after_item)


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
