from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import models, schemas
from app.utils.database import get_db
from app.auth.security import verify_password, create_access_token
import logging
from sqlalchemy.exc import SQLAlchemyError

# Set up logging for debugging purposes
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize password context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user by hashing their password and storing them in the database.
    """
    try:
        # Check if the username already exists
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            logger.debug(f"Username {user.username} already exists in the database.")
            raise HTTPException(status_code=400, detail="Username already registered")

        # Hash the user's password
        hashed_password = pwd_context.hash(user.password)
        logger.debug(f"Hashed password for {user.username}.")

        # Create and add the new user to the database
        db_user = models.User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.debug(f"User {user.username} successfully registered.")
        return db_user

    except SQLAlchemyError as e:
        # Log and handle any database errors
        logger.error(f"Database error occurred during user registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error during registration")
    except Exception as e:
        # Catch any other unforeseen errors
        logger.error(f"Unexpected error occurred during user registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/token")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Log in a user by verifying their credentials and issuing a JWT token.
    """
    try:
        # Check if the user exists in the database
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if not db_user:
            logger.debug(f"Login failed: User {user.username} not found.")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Verify the password
        if not verify_password(user.password, db_user.hashed_password):
            logger.debug(f"Login failed: Incorrect password for {user.username}.")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        # Create an access token
        try:
            access_token = create_access_token(data={"sub": db_user.username})
            logger.debug(f"Access token generated for user {user.username}.")
        except Exception as e:
            logger.error(f"Error creating access token for {user.username}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

        # Return the token in the response
        return {"access_token": access_token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        # Log and handle any database errors
        logger.error(f"Database error occurred during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error during login")
    except Exception as e:
        # Catch any other unforeseen errors
        logger.error(f"Unexpected error occurred during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
