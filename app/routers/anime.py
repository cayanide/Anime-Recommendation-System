import httpx
from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AnimeSearchResult
from app.utils.database import get_db
from sqlalchemy.orm import Session
from app.models import UserPreference
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ANI_LIST_API_URL = "https://graphql.anilist.co/"

router = APIRouter()

async def get_anilist_data(query: str, variables: dict):
    async with httpx.AsyncClient() as client:
        try:
            # Set headers for GraphQL request (typically you need to specify Content-Type)
            headers = {
                "Content-Type": "application/json",
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

@router.get("/search")
async def search_anime(name: str, db: Session = Depends(get_db)):
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

    # Get the response from the Anilist API
    data = await get_anilist_data(query, variables)

    # Check if the necessary data exists before accessing it
    if not data or "data" not in data or "Page" not in data["data"] or "media" not in data["data"]["Page"]:
        logger.error(f"Invalid response structure: {data}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media from Anilist API")

    return data["data"]["Page"]["media"]

@router.get("/recommendations")
async def recommendations(db: Session = Depends(get_db)):
    # Fetch recommendations based on user's preferences or watched anime
    preferences = db.query(UserPreference).first()
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
    variables = {"genre": preferences.favorite_genre if preferences else "Action"}

    # Get the response from the Anilist API
    data = await get_anilist_data(query, variables)

    # Check if the necessary data exists before accessing it
    if not data or "data" not in data or "Page" not in data["data"] or "media" not in data["data"]["Page"]:
        logger.error(f"Invalid response structure: {data}")
        raise HTTPException(status_code=500, detail="Failed to retrieve media from Anilist API")

    return data["data"]["Page"]["media"]
