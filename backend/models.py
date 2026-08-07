from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UserSearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    searched_item = Column(String)  # Can store LeetCode username or problem name
    timestamp = Column(DateTime, default=datetime.utcnow)

    from sqlalchemy import Column, Integer, String
from database import Base

class UserLeaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    xp = Column(Integer, default=0)