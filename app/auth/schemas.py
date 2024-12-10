from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Schema for User Registration
class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username of the user")
    email: EmailStr = Field(..., description="Valid email address of the user")
    password: str = Field(..., min_length=6, max_length=100, description="Secure password for the user")
    favorite_genres: Optional[list[str]] = Field(
        default=[],
        description="List of favorite genres for personalized recommendations"
    )

# Schema for User Login
class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password for the user")

# Schema for Token Response
class TokenResponseSchema(BaseModel):
    access_token: str = Field(..., description="JWT access token for authenticated requests")
    token_type: str = Field(default="bearer", description="Type of the token")

# Schema for User Preferences
class UserPreferencesSchema(BaseModel):
    favorite_genres: Optional[list[str]] = Field(
        default=None,
        description="List of favorite genres for personalized recommendations"
    )
    watched_anime: Optional[list[int]] = Field(
        default=None,
        description="List of anime IDs the user has watched"
    )


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authenticated requests")
    token_type: str = Field(default="bearer", description="Type of the token")

# UserAuth Schema
class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
