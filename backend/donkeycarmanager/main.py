from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from donkeycarmanager import crud, models, schemas
from donkeycarmanager.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = crud.get_players(db, skip=skip, limit=limit)
    return players


@app.get("/player/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@app.post("/drivingWaitingQueue/", response_model=schemas.DrivingWaitingQueue)
def create_player(driving_waiting_queue: schemas.DrivingWaitingQueueCreate, db: Session = Depends(get_db)):
    # TODO check player_id isn't already in the waiting queue
    return crud.create_driving_waiting_queue(db=db, driving_waiting_queue=driving_waiting_queue)


@app.get("/drivingWaitingQueue/", response_model=List[schemas.DrivingWaitingQueue])
def read_players(by_rank: bool = True, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if by_rank:
        waiting_players = crud.get_driving_waiting_queue_by_rank(db, skip=skip, limit=limit)
    else:
        waiting_players = crud.get_driving_waiting_queue(db, skip=skip, limit=limit)
    return waiting_players


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
