# app/routers/anime.py

import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AnimeSearchResult
from app.utils.database import get_db
from sqlalchemy.orm import Session
from app.models.models import UserPreference
import logging
from app.auth.security import get_current_user


# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ANI_LIST_API_URL = "https://graphql.anilist.co/"

router = APIRouter()

# Add authorization check and token passing to requests
async def get_anilist_data(query: str, variables: dict, token: str):
    async with httpx.AsyncClient() as client:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",  # Pass the token here
            }

            # Send the POST request with the query and variables
            response = await client.post(ANI_LIST_API_URL, json={"query": query, "variables": variables}, headers=headers)

            # Log the full response for debugging
            logger.info(f"Anilist API response: {response.text}")

            # Raise an error if the response code is not 200 OK
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            # Log HTTP error details
            logger.error(f"Anilist API returned HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Anilist API error: {e.response.text}")
        except httpx.RequestError as e:
            # Handle network or other request errors
            logger.error(f"Error while making request to Anilist: {e}")
            raise HTTPException(status_code=500, detail=f"Error while making request to Anilist: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"An unexpected error occurred: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# Add the current_user dependency to ensure authentication
@router.get("/search")
async def search_anime(name: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    query = """
    query ($name: String) {
      Page(perPage: 10) {
        media(search: $name, type: ANIME) {
          id
          title {
            romaji
          }
          coverImage {
            medium
          }
        }
      }
    }
    """
    variables = {"name": name}

    # Get the response from the Anilist API using the token
    data = await get_anilist_data(query, variables, current_user["access_token"])

    if not data or "data" not in data or "Page" not in data["data"] or "media" not in data["data"]["Page"]:
        logger.error(f"Invalid response structure: {data}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media from Anilist API")

    return data["data"]["Page"]["media"]

@router.get("/recommendations")
async def recommendations(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # Fetch user preferences or use default preferences
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user["sub"]).first()

    if not preferences:
        logger.info(f"No preferences found for user {current_user['sub']}. Defaulting to 'Action' genre.")
        genre = "Action"  # Default genre
    else:
        genre = preferences.favorite_genre

    query = """
    query ($genre: String) {
      Page(perPage: 10) {
        media(genre: $genre, type: ANIME) {
          id
          title {
            romaji
          }
          coverImage {
            medium
          }
        }
      }
    }
    """
    variables = {"genre": genre}

    # Get the response from the Anilist API using the token
    data = await get_anilist_data(query, variables, current_user["access_token"])

    if not data or "data" not in data or "Page" not in data["data"] or "media" not in data["data"]["Page"]:
        logger.error(f"Invalid response structure: {data}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media from Anilist API")

    return data["data"]["Page"]["media"]
