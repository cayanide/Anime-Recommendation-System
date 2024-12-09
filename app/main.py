#app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.requests import Request
from dotenv import load_dotenv
import os

from app.routers import anime, auth, user
from app.utils.database import Base, engine

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Serve static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="app/templates"), name="static")

# Initialize Jinja2 template rendering
templates = Jinja2Templates(directory="app/templates")

# Include routers for anime, authentication, and user endpoints
app.include_router(anime.router, prefix="/anime", tags=["Anime"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["User"])

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """
    Serve the index.html as the homepage.
    """
    return templates.TemplateResponse("index.html", {"request": request})
