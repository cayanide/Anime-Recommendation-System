import datetime
from datetime import timedelta
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.database import get_db
import os
from dotenv import load_dotenv
import logging  # Import logging module

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # You can adjust the level (e.g., INFO, DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in the environment variables.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Password Bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """Create a JWT token with an expiration date."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta  # Use datetime.datetime to fix the 'utcnow' error
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get the current authenticated user based on the JWT token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    logger.debug(f"Received token: {token}")  # Log the received token

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Fetch user from the database
        user = db.query(User).filter(User.username == username).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except jwt.PyJWTError as e:
        logger.error(f"Error decoding token: {e}")  # Log the error message
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# OAuth2 Login Route
router = APIRouter()

@router.post("/token")
async def login(request: dict, db: Session = Depends(get_db)):
    """
    Login route to authenticate users and return a JWT token.
    The `request` should contain `username` and `password`.
    """
    username = request.get("username")
    password = request.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    # Fetch user from the database
    user = db.query(User).filter(User.username == username).first()

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate the JWT token
    access_token = create_access_token(data={"sub": user.username})

    logger.debug(f"Generated token: {access_token}")  # Log the generated token

    return {"access_token": access_token, "token_type": "bearer"}

# Password Hashing Function (for Registration)
def hash_password(password: str) -> str:
    """Hash the user's password before storing it in the database."""
    return pwd_context.hash(password)

# Example Register User function (for reference)
def create_user(db: Session, username: str, password: str) -> User:
    """
    Creates a new user with hashed password.
    Should be used during registration or user creation.
    """
    hashed_password = hash_password(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Optional: Example of Register Route (for completeness)
@router.post("/register")
async def register(request: dict, db: Session = Depends(get_db)):
    """
    Register route to create a new user. The `request` should contain `username` and `password`.
    """
    username = request.get("username")
    password = request.get("password")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password are required")

    # Check if the username is already taken
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Create and save the new user
    user = create_user(db, username, password)
    return {"message": "User created successfully", "username": user.username}
