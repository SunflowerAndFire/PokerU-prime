import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column

class Game(SQLModel, table=True):
    __tablename__ = "games"

    uid: uuid.UUID=Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    game_time: datetime = Field(sa_column=Column(pg.TIMESTAMP))
    location: str
    buy_in: int
    host: str
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<Game {self.title}>"
    