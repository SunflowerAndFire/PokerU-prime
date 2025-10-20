from pydantic import BaseModel

class GameCreateModel(BaseModel):
    title: str
    game_time: str
    location: str
    buy_in: int
    host: str
    
class GameUpdateModel(BaseModel):
    title: str
    game_time: str
    location: str
    buy_in: int
