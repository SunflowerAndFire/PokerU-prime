from fastapi import FastAPI

from .config import Config
from .auth.routes import auth_router
from .games.routes import game_router

api_version = Config.VERSION

app = FastAPI(
    title="PokerU Mobile App",
    description="REST APIs for a college poker social media platform",
    version=api_version
)

app.include_router(auth_router, prefix=f"/api/{api_version}/auth", tags=['auth'])
app.include_router(game_router, prefix=f"/api/{api_version}/games", tags=['games'])