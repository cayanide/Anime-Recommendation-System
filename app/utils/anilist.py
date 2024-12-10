import httpx
import os
from typing import List

BASE_URL = "https://graphql.anilist.co"

async def fetch_anilist_data(query: str, variables: dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('ANILIST_CLIENT_ID')}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        return response.json()

async def search_anime(query: str, genre: str = None):
    """Search for anime by name or genre."""
    search_query = """
    query ($search: String, $genre: String) {
        Page {
            media(search: $search, genre: $genre, type: ANIME) {
                id
                title {
                    romaji
                }
                genres
            }
        }
    }
    """
    variables = {"search": query, "genre": genre}
    data = await fetch_anilist_data(search_query, variables)
    return data["data"]["Page"]["media"]

async def get_recommendations(preferences: List[str]):
    """Fetch anime recommendations based on genres."""
    recommendations_query = """
    query ($genres: [String]) {
        Page {
            media(genre_in: $genres, type: ANIME, sort: POPULARITY_DESC) {
                id
                title {
                    romaji
                }
                genres
            }
        }
    }
    """
    variables = {"genres": preferences}
    data = await fetch_anilist_data(recommendations_query, variables)
    return data["data"]["Page"]["media"]
