import uuid
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Field, Column, LargeBinary

domain_of_college = {
    "tulane.edu": "Tulane University",
    "gsu.edu": "Georgia State University",
}

class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID=Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    username: str
    email: str
    hashed_password: bytes = Field(sa_column=Column(LargeBinary), exclude=True)
    college: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="basic_user")
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self):
        return f"<User {self.username}>"
