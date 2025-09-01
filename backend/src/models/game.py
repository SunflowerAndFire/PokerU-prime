from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base

class Game(Base):
    __tablename__ = "games"

    '''
    Other model's attributes:
    id = Column(Integer, primary_key=True, index=True)
    '''

    pass
