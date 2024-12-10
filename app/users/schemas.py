#app/users/schemas.py
from pydantic import BaseModel
from typing import Optional

# Schema for user preferences
class UserPreferences(BaseModel):
    preferences: str

    class Config:
        orm_mode = True  # This allows Pydantic models to work with SQLAlchemy models directly

# Schema for user creation (if needed)
class UserCreate(BaseModel):
    username: str
    password: str  # Plain password, will be hashed in the service layer

    class Config:
        orm_mode = True

# Schema for the user response (without password)
class UserResponse(BaseModel):
    username: str

    class Config:
        orm_mode = True
