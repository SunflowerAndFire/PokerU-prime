from datetime import datetime
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Game
from .schemas import GameCreateModel, GameUpdateModel

class GameService:
    async def get_all_games(self, session: AsyncSession):
        statement = select(Game).order_by(desc(Game.created_at))
        result = await session.exec(statement)
        return result.all()
    
    async def get_game(self, game_uid: str, session: AsyncSession):
        statement = select(Game).where(Game.uid == game_uid)
        
        result = await session.exec(statement)
        game = result.first()

        return game if game is not None else None

    async def create_game(self, game_data: GameCreateModel, session: AsyncSession):
        game_data_dict = game_data.model_dump()
        new_game = Game(
            **game_data_dict
        )

        new_game.game_time = datetime.strptime(game_data_dict["game_time"], "%Y-%m-%d %H:%M")

        session.add(new_game)
        await session.commit()
        return new_game
    
    async def update_game(self, game_uid: str, game_data: GameUpdateModel, session: AsyncSession):
        game_to_update = await self.get_game(game_uid, session)

        if game_to_update is not None:
            update_data_dict = game_data.model_dump()
            
            for key, val in update_data_dict.items():
                value = val
                if key == "game_time":
                    value = datetime.strptime(update_data_dict["game_time"], "%Y-%m-%d %H:%M")

                setattr(game_to_update, key, value)

            await session.commit()
            return game_to_update

        return None

    async def delete_game(self, game_uid: str, session: AsyncSession):
        game_to_delete = await self.get_game(game_uid, session)

        if game_to_delete is not None:
            await session.delete(game_to_delete)
            await session.commit()
            return "Game deleted successfully"

        return None
    