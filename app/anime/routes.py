from fastapi import APIRouter, Depends, HTTPException, status
from utils.anilist import search_anime, get_recommendations
from utils.token import decode_access_token
from database.models import User
from sqlalchemy.future import select
from database.config import async_session

anime_router = APIRouter()

@anime_router.get("/search")
async def search_anime_route(query: str, genre: str = None):
    """Search anime by name or genre"""
    try:
        results = await search_anime(query=query, genre=genre)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@anime_router.get("/recommendations")
async def get_recommendations_route(token: str = Depends(decode_access_token)):
    """Fetch recommendations for a user based on their preferences."""
    username = token.get("sub")
    async with async_session() as session:
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        db_user = result.scalars().first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        preferences = db_user.preferences
        if not preferences:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Preferences not set")

        try:
            recommendations = await get_recommendations(preferences.split(","))
            return {"recommendations": recommendations}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
