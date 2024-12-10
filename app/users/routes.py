#app/users/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import update
from utils.token import decode_access_token
from database import get_db
from database.models import User
from users.schemas import UserPreferences
from auth.dependencies import get_current_user

user_router = APIRouter()

@user_router.get("/preferences")
async def get_preferences(token: str = Depends(decode_access_token), db: AsyncSession = Depends(get_db)):
    """Get user preferences."""
    username = token.get("sub")
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"preferences": db_user.preferences or ""}

@user_router.post("/preferences")
async def update_preferences(preferences: str, token: str = Depends(decode_access_token), db: AsyncSession = Depends(get_db)):
    """Update user preferences."""
    username = token.get("sub")
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    async with db.begin():
        stmt = update(User).where(User.username == username).values(preferences=preferences)
        await db.execute(stmt)
    await db.commit()
    return {"message": "Preferences updated successfully"}
