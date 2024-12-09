from pydantic import BaseModel
from typing import List, Optional, Dict

# -----------------------------
# User-related schemas
# -----------------------------

# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    username: str
    password: str

# Schema for user login, returning JWT token
class UserLogin(BaseModel):
    username: str
    password: str

# Schema for the response after successful login (with token)
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str

# Schema for managing user preferences (e.g., favorite genres)
class PreferenceCreate(BaseModel):
    genre: str

class UserPreferences(BaseModel):
    user_id: int
    genres: List[str]  # List of user's favorite genres

# Schema to represent a User
class User(BaseModel):
    id: int  # Assuming the user has an ID in the database
    username: str
    # You can add other fields here based on your database model (e.g., email, created_at, etc.)

# -----------------------------
# Anime-related schemas
# -----------------------------

# Anime object schema for holding anime data fetched from AniList API
class AnimeResponse(BaseModel):
    id: Optional[int]  # Optional id for each anime (can be used as a reference)
    title: Optional[Dict[str, str]]  # Title in multiple languages (romaji, english, native)
    genres: List[str]  # List of genres
    description: Optional[str] = None  # Optional description for the anime
    image_url: Optional[str] = None  # Optional image URL for the anime

# Anime search response schema for returning the list of anime results
class AnimeSearchResponse(BaseModel):
    results: List[AnimeResponse]  # List of AnimeResponse objects as search results

# Schema for Anime recommendations based on user preferences
class AnimeRecommendation(BaseModel):
    title: str
    image_url: Optional[str] = None
    score: Optional[float] = None
    description: Optional[str] = None  # Optional description for recommendations

class AnimeRecommendationResponse(BaseModel):
    recommendations: List[AnimeRecommendation]  # List of recommended anime

# -----------------------------
# Schemas for handling anime data (CRUD operations)
# -----------------------------

# Anime create schema for handling new anime data (e.g., adding anime to a database)
class AnimeCreate(BaseModel):
    title: str
    genre: str
    description: Optional[str] = None  # Optional field for description

# -----------------------------
# General response schema for API errors
# -----------------------------

class ErrorResponse(BaseModel):
    detail: str  # For general error messages

class AnimeSearchResult(BaseModel):
    id: Optional[int]  # Anime ID
    title: Optional[Dict[str, str]]  # Title in multiple languages (romaji, english, native)
    image: Optional[Dict[str, str]]  # Image details (medium image URL)

# Define the response schema for the search results
class AnimeSearchResponse(BaseModel):
    results: List[AnimeSearchResult]  # List of anime search results
