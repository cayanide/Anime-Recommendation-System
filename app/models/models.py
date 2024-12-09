from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Added length limit
    email = Column(String(100), unique=True, index=True)    # Added length limit
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)  # Added created_at timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at timestamp

    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")  # Cascade delete for preferences
    watched_anime = relationship("WatchedAnime", back_populates="owner", cascade="all, delete-orphan")  # Cascade delete for watched_anime

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    favorite_genre = Column(String, nullable=True)  # Marked nullable for optional field

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(id={self.id}, user_id={self.user_id}, favorite_genre={self.favorite_genre})>"

class WatchedAnime(Base):
    __tablename__ = "watched_anime"

    id = Column(Integer, primary_key=True, index=True)
    anime_title = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="watched_anime")

    def __repr__(self):
        return f"<WatchedAnime(id={self.id}, anime_title={self.anime_title})>"
