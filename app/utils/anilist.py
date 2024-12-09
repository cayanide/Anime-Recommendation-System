#app/utils/anilist.py

import os
import httpx  # Use httpx for asynchronous requests
from typing import List, Dict

# Assuming you have these environment variables set
CLIENT_ID = os.getenv("ANILIST_CLIENT_ID")
CLIENT_SECRET = os.getenv("ANILIST_CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")
API_URL = "https://graphql.anilist.co"

# Helper function to get the access token
async def get_access_token(code: str) -> Dict:
    token_url = "https://anilist.co/api/v2/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URL,
        "code": code
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        return response.json()

# Function to query AniList GraphQL API with a given query
async def fetch_from_anilist(query: str, variables: Dict = None) -> Dict:
    headers = {
        "Content-Type": "application/json",
    }
    data = {"query": query, "variables": variables} if variables else {"query": query}

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

# Function to fetch anime by name using AniList API
async def get_anime_by_name(name: str) -> List[Dict]:
    query = """
    query ($search: String) {
        Page(perPage: 5) {
            media(search: $search, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                genres
                description
            }
        }
    }
    """
    variables = {"search": name}
    data = await fetch_from_anilist(query, variables)
    return data.get("data", {}).get("Page", {}).get("media", [])

# Function to fetch anime by genre using AniList API
async def get_anime_by_genre(genre: str) -> List[Dict]:
    query = """
    query ($genre: String) {
        Page(perPage: 5) {
            media(genre: $genre, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                genres
                description
            }
        }
    }
    """
    variables = {"genre": genre}
    data = await fetch_from_anilist(query, variables)
    return data.get("data", {}).get("Page", {}).get("media", [])

# Function to fetch recommended anime based on user preferences (genre in this case)
async def get_recommended_anime(user_preferences: List[str]) -> List[Dict]:
    query = """
    query ($genres: [String]) {
        Page(perPage: 5) {
            media(genre_in: $genres, type: ANIME) {
                id
                title {
                    romaji
                    english
                    native
                }
                genres
                description
            }
        }
    }
    """
    variables = {"genres": user_preferences}
    data = await fetch_from_anilist(query, variables)
    return data.get("data", {}).get("Page", {}).get("media", [])
