from typing import List
from fastapi.exceptions import HTTPException
from fastapi import status, APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.auth.dependencies import RoleChecker, AccessTokenBearer

from .models import Game
from .service import GameService
from .schemas import GameCreateModel, GameUpdateModel

game_router = APIRouter()
game_service = GameService()
access_token_bearer = Depends(AccessTokenBearer())
role_checker = Depends(RoleChecker(["admin", "staff", "basic_user", "premium_user"]))

@game_router.get(
    "/", 
    response_model=List[Game], 
    dependencies=[access_token_bearer, role_checker]
)
async def get_all_games(
    session: AsyncSession = Depends(get_session)
):
    """Return all games in our DB"""
    games = await game_service.get_all_games(session)
    return games

@game_router.get(
    "/{game_uid}",
    response_model=Game,
    dependencies=[access_token_bearer, role_checker]
)
async def get_game(
    game_uid: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a game based on its uid"""
    game = await game_service.get_game(game_uid, session)
    if game:
        return game
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

@game_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Game,
    dependencies=[access_token_bearer, role_checker]
)
async def create_game(
    game_data: GameCreateModel,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """Host game with title and host information"""
    new_game = await game_service.create_game(game_data, session)
    return new_game

@game_router.patch(
    "/{game_uid}",
    response_model=Game,
    dependencies=[access_token_bearer, role_checker]
)
async def update_game(
    game_uid: str,
    game_update_data: GameUpdateModel,
    session: AsyncSession = Depends(get_session)
):
    """Update game based on its id with new information"""
    game_to_update = await game_service.update_game(game_uid, game_update_data, session)
    
    if game_to_update:
        return game_to_update
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

@game_router.delete(
    "/{game_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[access_token_bearer, role_checker]
)
async def delete_game(
    game_uid: str,
    session: AsyncSession = Depends(get_session)
):
    """Delete a game based on its id"""
    game_to_delete = await game_service.delete_game(game_uid, session)
    
    if game_to_delete:
        return {}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
