from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request
from dotenv import load_dotenv
import os

# Correct imports based on your directory structure
from app.routers import anime
from app.auth import auth
from app.routers.user_router import router as user_router
from app.utils.database import Base, engine
from app.auth.security import get_current_user  # Import the security functions for authentication

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create database tables (using SQLAlchemy)
Base.metadata.create_all(bind=engine)

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="app/static"), name="static")  # Adjusted path

# Initialize Jinja2 template rendering for HTML pages
templates = Jinja2Templates(directory="app/templates")

# Include routers for anime, authentication, and user endpoints
app.include_router(anime.router, prefix="/anime", tags=["Anime"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])  # Including auth router
app.include_router(user_router, prefix="/user", tags=["User"])  # Including user router

# Route for the homepage (index.html)
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve the index.html as the homepage for users who aren't logged in.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Route for the user's dashboard page (home.html)
@app.get("/home.html", response_class=HTMLResponse)
async def get_home(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Serve the home.html page for logged-in users.
    This page is accessible only if the user is authenticated.
    """
    if current_user is None:
        # If no current user, raise an unauthorized error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return templates.TemplateResponse("home.html", {"request": request, "user": current_user})

# Route for the token page (test.html)
@app.get("/test.html", response_class=HTMLResponse)
async def get_test(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Serve the test.html page with token info and the username.
    This page is accessible only if the user is authenticated.
    """
    if current_user is None:
        # If no current user, raise an unauthorized error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return templates.TemplateResponse("test.html", {"request": request, "user": current_user})

# Route for anime page (anime.html)
@app.get("/anime.html", response_class=HTMLResponse)
async def get_anime(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Serve the anime.html page.
    This page is accessible only if the user is authenticated.
    """
    if current_user is None:
        # If no current user, raise an unauthorized error
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return templates.TemplateResponse("anime.html", {"request": request, "user": current_user})

# Logout route
@app.get("/logout")
async def logout():
    """
    Log the user out by clearing the access token and redirecting to the login page.
    """
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")  # Optional: Delete cookie if used for authentication
    return response
