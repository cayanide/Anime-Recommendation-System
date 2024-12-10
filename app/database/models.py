from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
Base = declarative_base()
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
# User model - Includes a relationship with UserPreferences
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Relationship with UserPreferences (one-to-one)
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)

    # Relationship with AnimeCache (one-to-many)
    anime_cache = relationship("AnimeCache", back_populates="user")


# UserPreferences model - Stores user's favorite genres and other preferences
class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Corrected ForeignKey reference
    favorite_genres = Column(String)  # Comma-separated genres or JSON format

    # Relationship back to the User model
    user = relationship("User", back_populates="preferences")


# AnimeCache model - Stores anime cache data for users
class AnimeCache(Base):
    __tablename__ = "anime_cache"

    id = Column(Integer, primary_key=True, index=True)
    anime_id = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    genre = Column(Text, nullable=True)
    cached_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # Use DateTime type for timestamps

    # Link to User model (one-to-many: a user can have multiple cached anime)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Nullable in case the anime is not linked to a user

    # Relationship with User model
    user = relationship("User", back_populates="anime_cache")



class UserBase(BaseModel):
    id: int
    username: str
    email: str  # Make sure email is part of the Pydantic model

    class Config:
        orm_mode = True




class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str

    # This enables support for SQLAlchemy models
    class Config:
        orm_mode = True
