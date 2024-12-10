from fastapi import Depends, HTTPException, status
from app.utils.token import decode_access_token
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User  # Assuming User model is here

async def get_current_user(token: str = Depends(decode_access_token), db: AsyncSession = Depends(get_db)):
    """Retrieve the current user from the token."""
    username = token.get("sub")  # Assuming 'sub' is the user identifier in the token
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Query the user from the database
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
