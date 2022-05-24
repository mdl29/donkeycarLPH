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

