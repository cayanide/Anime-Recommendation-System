from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Load environment variables
load_dotenv()

# Configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 45
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
ANILIST_CLIENT_ID = os.getenv("ANILIST_CLIENT_ID")
ANILIST_CLIENT_SECRET = os.getenv("ANILIST_CLIENT_SECRET")
REDIRECT_URL = os.getenv("REDIRECT_URL")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    preferences = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Preferences(BaseModel):
    favorite_genres: list[str]

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Jinja2 Templates setup
templates = Jinja2Templates(directory="app/templates")

# OAuth2 PasswordBearer for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Token generation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency for getting the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Helper function to query AniList's GraphQL API
def aniList_graphql(query: str, variables: dict = None):
    url = "https://graphql.anilist.co"
    headers = {"Content-Type": "application/json"}

    payload = {
        "query": query,
        "variables": variables or {}
    }

    # Log the query and variables for debugging
    print("Sending request to AniList API:")
    print("Query:", query)
    print("Variables:", variables)

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()  # Return the JSON response if successful
    except requests.exceptions.RequestException as e:
        # Log the error for debugging
        print(f"Error making request to AniList API: {e}")
        return None  # Return None if the request fails

# GraphQL query for searching anime
def search_anime_query(query: str):
    return """
    query ($search: String) {
      Page(page: 1, perPage: 10) {
        media(search: $search, type: ANIME) {
          id
          title {
            romaji
            english
            native
          }
          coverImage {
            large
          }
        }
      }
    }
    """

# GraphQL query for fetching recommendations

# Routes
@app.get("/")
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Anime Search Route
@app.get("/anime/search")
async def search_anime(request: Request, query: str):
    graphql_query = search_anime_query(query)
    response = aniList_graphql(graphql_query, {"search": query})
    search_results = response.get("data", {}).get("Page", {}).get("media", [])
    return {"searchResults": search_results}

# Fetch Recommendations Route
#
#



# GraphQL query for fetching recommendations
def get_recommendations_query():
    return """
    query {
      MediaTrend(mediaType: ANIME) {
        media {
          id
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

# Fetch Recommendations Route
@app.get("/anime/recommendations")
async def fetch_recommendations(request: Request, genres: str = None, current_user: User = Depends(get_current_user)):
    # Use the genres passed in the query params or fetch from the user's preferences if not provided
    if genres is None:
        favorite_genres = current_user.preferences
        if not favorite_genres:
            raise HTTPException(status_code=400, detail="User has no preferences set")
        genres_list = favorite_genres.split(",")
    else:
        genres_list = genres.split(",")

    # Construct a query to search for anime based on these genres
    graphql_query = get_recommendations_query()  # No need to pass genres here for the recommendations query

    # Call AniList API to get recommendations
    response = aniList_graphql(graphql_query)  # No need to pass any variables for the recommendations

    if not response:
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations from AniList API")

    recommendations = response.get("data", {}).get("MediaTrend", [])

    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return {"recommendations": recommendations}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/dashboard/data")
async def dashboard_data(current_user: User = Depends(get_current_user)):
    # Returning the user details as a response
    return {"user": {"username": current_user.username, "preferences": current_user.preferences}, "token": "Bearer " + create_access_token(data={"sub": current_user.username})}

@app.get("/home.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



@app.get("/user/token")
def get_user_token(current_user: User = Depends(get_current_user)):
    return {"token": "Bearer " + create_access_token(data={"sub": current_user.username})}


def update_preferences():
    favorite_genres = request.form.get('favorite_genres')
    # Process and save the preferences (e.g., to the database or session)
    user = get_current_user()  # Assuming you have a function to get the logged-in user
    user.favorite_genres = favorite_genres.split(",")  # Store genres as a list
    save_user(user)  # Save updated preferences
    return redirect('/recommendations')

@app.route('/anime/recommendations')
def get_recommendations():
    user = get_current_user()  # Get the current user
    favorite_genres = user.favorite_genres  # Retrieve favorite genres
    recommendations = fetch_recommendations_based_on_genres(favorite_genres)
    return jsonify(recommendations)

# Fetch Recommendations Route based on user's preferences

@app.get("/anime/recommendations")
async def fetch_recommendations(
    genres: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if genres is provided or fall back to the user's preferences
    if genres is None:
        favorite_genres = current_user.preferences
        if not favorite_genres:
            raise HTTPException(status_code=400, detail="User has no preferences set")
        genres_list = favorite_genres.split(",")
    else:
        genres_list = genres.split(",")

    # Construct query to search for anime based on these genres
    graphql_query = search_anime_query(' '.join(genres_list))  # Using genres list for search query

    # Call AniList API to get recommendations
    response = aniList_graphql(graphql_query)

    if not response:
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations from AniList API")

    recommendations = response.get("data", {}).get("Page", {}).get("media", [])

    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")

    return {"recommendations": recommendations}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
