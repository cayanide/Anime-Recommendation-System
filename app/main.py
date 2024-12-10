#app/main.py
from sqlalchemy.orm import sessionmaker
import os
import secrets
import jwt
from fastapi import FastAPI, Form, Request, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from dotenv import load_dotenv
from database.models import User
from database.models import UserBase
from database.models import UserPreferences
from database.models import UserOut
from database.models import UserIn
from passlib.context import CryptContext
from auth.services import create_user
import httpx
from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

# Load environment variables from the .env file
load_dotenv()

# Get the values from the .env file
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Initialize the database connection for async operations
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# JWT Secret and Algorithm
SECRET_KEY = secrets.token_urlsafe(32)  # Random secret key for JWT
ALGORITHM = "HS256"  # JWT algorithm

# Initialize FastAPI application
app = FastAPI(
    title="Anime Recommendation System",
    description="A REST API to manage anime recommendations, search, and user preferences using AniList API.",
    version="1.0.0",
)

# Add SessionMiddleware with the generated secret key
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Jinja2 Templates for rendering HTML
templates = Jinja2Templates(directory="templates")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Static Files from templates directory (CSS, JS)
static_dir = "templates"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print(f"Error: The static directory '{static_dir}' does not exist.")

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

@app.get("/users/{user_id}", response_model=UserBase)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Ensure async session is being used correctly
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert SQLAlchemy object to Pydantic model before returning
    return UserBase.from_orm(user)


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn, db: AsyncSession = Depends(get_db)):
    # Create a new user and save it to the database
    db_user = User(username=user.username, hashed_password=user.password)  # Adjust this line according to your model
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Return the created user as a Pydantic model
    return UserOut.from_orm(db_user)
# Create database tables on startup (asynchronously)
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # This will create all tables
        await conn.run_sync(Base.metadata.create_all)

# Root route for landing page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Function to verify credentials
async def verify_credentials(db, username: str, password: str):
    # Fetch user from the database
    stmt = select(User).filter(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user and pwd_context.verify(password, user.hashed_password):  # Use hashed_password here
        return user
    return None

# Function to generate a JWT token
def create_token(user_id: int, username: str):
    payload = {"sub": username, "user_id": user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Login route (with session handling)
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    async with AsyncSessionLocal() as db:
        # Check if user credentials are valid by querying the PostgreSQL database
        user = await verify_credentials(db, username, password)

        if user:
            # Generate JWT token
            token = create_token(user.id, user.username)

            # Store user info and token in session
            request.session["user"] = user.username
            request.session["token"] = token

            return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Dashboard route (after login)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    token = request.session.get("token")  # Retrieve the token from the session

    if user and token:
        return templates.TemplateResponse("dashboard.html", {"request": request, "token": token})
    else:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Logout route to clear the session
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()  # Clear the session
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Route to show the registration form (GET request)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Route to handle user registration (POST request)
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash the password before creating the user
    hashed_password = pwd_context.hash(password)

    # Create the user
    user = {
        "username": username,
        "password": hashed_password
    }
    await create_user(user)
    return {"message": "User registered successfully"}

ANILIST_API_URL = "https://graphql.anilist.co"
router = APIRouter()

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> UserOut:
    return use
# Helper function to fetch anime data from AniList API
#


@app.get("/user/preferences", response_model=UserOut)
async def get_user_preferences(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user  # This will automatically be serialized using UserOut model



@router.get("/api/anime_recommendations")


# Fixing the route for anime recommendations
@router.get("/api/anime_recommendations", response_model=dict)
async def get_anime_recommendations(user_id: int, db_session: AsyncSession = Depends(get_db)):
    """
    Fetch anime recommendations based on the user's preferences.
    """
    # Fetch user preferences dynamically
    genres = await get_user_preferences(user_id, db_session)

    if not genres:
        return {"recommendations": []}

    # Constructing the AniList API query using user preferences
    query = """
    query ($genres: [String]) {
      Page {
        media(genre_in: $genres) {
          title {
            romaji
            english
          }
          coverImage {
            large
          }
        }
      }
    }
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(ANILIST_API_URL, json={"query": query, "variables": {"genres": genres}})
        data = response.json()

    recommendations = []
    if "data" in data and "Page" in data["data"]:
        recommendations = data["data"]["Page"]["media"]

    return {"recommendations": recommendations}

# Home page route that displays recommendations and search functionality
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch anime recommendations by passing 'request'
    recommendations = await fetch_anime_recommendations(request)

    return templates.TemplateResponse("home.html", {"request": request, "user": user, "recommendations": recommendations})

# Add a search API endpoint for searching anime
@app.get("/search")
async def search(request: Request, query: str):
    search_results = await search_anime(query)  # Function to fetch search results from AniList API
    return templates.TemplateResponse("home.html", {"request": request, "user": request.session.get("user"), "search_results": search_results})

# Helper function to search anime via AniList API
# Search for anime by query
@router.get("/api/search")
async def search_anime(query: str):
    search_query = """
    query ($query: String) {
      Page {
        media(search: $query) {
          title {
            romaji
          }
          coverImage {
            large
          }
        }
      }
    }
    """

    variables = {"query": query}

    async with httpx.AsyncClient() as client:
        response = await client.post(ANILIST_API_URL, json={"query": search_query, "variables": variables})
        data = response.json()

    search_results = []
    if "data" in data and "Page" in data["data"] and "media" in data["data"]["Page"]:
        search_results = data["data"]["Page"]["media"]

    return {"searchResults": search_results}





async def get_user_by_id(user_id: str, session: AsyncSession) -> User:
    result = await session.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    return user

@app.post("/user/preferences")
async def set_user_preferences(request: Request, favorite_genres: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=403, detail="User not authenticated")

    # Fetch the user ID from the session or from the database
    stmt = select(User).filter(User.username == user)
    result = await db.execute(stmt)
    user_obj = result.scalars().first()

    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    # Proceed with fetching and updating the user preferences
    stmt = select(UserPreferences).filter(UserPreferences.user_id == user_obj.id)
    result = await db.execute(stmt)
    preferences = result.scalars().first()

    if preferences:
        preferences.favorite_genres = favorite_genres  # Update existing preferences
    else:
        # Create new preferences record
        preferences = UserPreferences(user_id=user_obj.id, favorite_genres=favorite_genres)
        db.add(preferences)

    await db.commit()
    return {"message": "Preferences updated successfully"}


# main.py

@app.get("/anime/recommendations")
async def fetch_anime_recommendations(request: Request):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=403, detail="User not authenticated")

    # Fetch user data and preferences asynchronously
    async with AsyncSessionLocal() as db:
        stmt = select(User).filter(User.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch preferences
    stmt = select(UserPreferences).filter(UserPreferences.user_id == user.id)
    result = await db.execute(stmt)
    preferences = result.scalars().first()

    if not preferences or not preferences.favorite_genres:
        raise HTTPException(status_code=404, detail="User preferences not set")

    # Fetch recommendations from AniList API
    recommendations = await fetch_anime_recommendations_by_genres(preferences.favorite_genres.split(","))

    return {"recommendations": recommendations}  # Return the recommendations as a dictionary

# Helper function to fetch anime recommendations based on genres
async def fetch_anime_recommendations_by_genres(favorite_genres: list):
    genre_queries = ",".join([f'"{genre}"' for genre in favorite_genres])
    query = f"""
    query {{
      Page {{
        media(genre_in: [{genre_queries}]) {{
          title {{
            romaji
          }}
          coverImage {{
            large
          }}
        }}
      }}
    }}
    """

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ANILIST_API_URL, json={"query": query})
            response.raise_for_status()  # Raise an error for bad HTTP status
            data = response.json()

            recommendations = []
            if data and "data" in data and "Page" in data["data"]:
                recommendations = data["data"]["Page"]["media"]
            else:
                print("Unexpected response structure or missing data.")
            return {"recommendations": recommendations}
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return {"recommendations": []}
        except Exception as e:
            print(f"Error processing response: {e}")
            return {"recommendations": []}

# New route to display the recommendations page
@app.get("/recommendations", response_class=HTMLResponse)
@app.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(request: Request):
    username = request.session.get("user")  # Retrieve logged-in username
    if not username:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch user data
    async with AsyncSessionLocal() as db:
        stmt = select(User).filter(User.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user.id  # Get the user ID here

    # Fetch preferences and recommendations
    async with AsyncSessionLocal() as db:
        stmt = select(UserPreferences).filter(UserPreferences.user_id == user_id)
        result = await db.execute(stmt)
        preferences = result.scalars().first()

        if not preferences or not preferences.favorite_genres:
            return templates.TemplateResponse(
                "recommendations.html",
                {"request": request, "user": username, "recommendations": [], "error": "No preferences set."},
            )

    # Pass correct user_id to fetch recommendations
    genres = preferences.favorite_genres.split(",")
    recommendations = await fetch_anime_recommendations_by_genres(genres)

    return templates.TemplateResponse(
        "recommendations.html",
        {"request": request, "user": username, "recommendations": recommendations},
    )



@app.get("/api/anime_recommendations")
async def get_recommendations(user_id: int = Query(...)):
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    # Handle the recommendation logic here
    return {"message": "Recommendations for user {}".format(user_id)}

AsyncSessionFactory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Example of handling a session properly with async context manager
async def get_user_preferences(user_id: int):
    async with AsyncSessionFactory() as session:
        async with session.begin():  # This ensures the connection is committed/rolled back
            result = await session.execute(
                "SELECT user_preferences.id, user_preferences.user_id, user_preferences.favorite_genres "
                "FROM user_preferences WHERE user_preferences.user_id = :user_id",
                {"user_id": user_id}
            )
            return result.fetchall()

def add_anime_preference(user_id, anime_title, anime_cover_image, action):
    conn = sqlite3.connect('anime_preferences.db')  # Use your project database connection
    cursor = conn.cursor()

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO AnimePreferences (user_id, anime_title, anime_cover_image, preference_action, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, anime_title, anime_cover_image, action, created_at))

    conn.commit()
    conn.close()

def remove_anime_preference(user_id, anime_title):
    conn = sqlite3.connect('anime_preferences.db')  # Use your project database connection
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE AnimePreferences
        SET preference_action = 'remove', created_at = ?
        WHERE user_id = ? AND anime_title = ? AND preference_action = 'add'
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id, anime_title))

    conn.commit()
    conn.close()


def get_user_preferences(user_id):
    conn = sqlite3.connect('anime_preferences.db')  # Use your project database connection
    cursor = conn.cursor()

    cursor.execute('''
        SELECT anime_title, anime_cover_image, preference_action
        FROM AnimePreferences
        WHERE user_id = ?
    ''', (user_id,))
    preferences = cursor.fetchall()

    conn.close()
    return preferences



app.include_router(router)
