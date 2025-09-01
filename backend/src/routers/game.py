import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks

from db.database import get_db, SessionLocal
from models.game import Game
from schemas.game import (
    GameBase
)

router = APIRouter(
    prefix="/games",
    tags=["games"]
)

@router.post("/create", response_model="")
def create_game(
    request: Game, # placeholder
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: Game, # placeholder
    db: Session = Depends(get_db)
):
    pass
