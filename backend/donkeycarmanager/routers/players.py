from typing import List, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from donkeycarmanager import schemas
import donkeycarmanager.crud.players as crud
from donkeycarmanager.dependencies import get_db

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)


@router.post("/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_pseudo(db, player_pseudo=player.player_pseudo)
    if db_player:
        raise HTTPException(status_code=400, detail="Pseudo already registered")
    return crud.create_player(db=db, player=player)


@router.get("/", response_model=List[schemas.Player])
def read_players(player_pseudo: Union[str, None] = Query(
        default=None,
        description="Will get a list a player matching this pseudo, as pseudo are unique "
                    "it should at most return one player."
    ),
        skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    if player_pseudo:
        return [crud.get_player_by_pseudo(db, player_pseudo=player_pseudo)]

    return crud.get_players(db, skip=skip, limit=limit)


@router.get("/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player


@router.put("/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, player: schemas.Player, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return crud.update_player(db, player=player)
