from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Fetch required database configuration from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Check if all required environment variables are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    logger.error("Missing required database environment variables.")
    raise EnvironmentError("Missing required database environment variables.")

# Construct the PostgreSQL URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine and log the connection attempt
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Try to connect to the database to validate the connection
    with engine.connect() as connection:
        logger.info("Successfully connected to the database.")
except Exception as e:
    logger.error(f"Error connecting to the database: {e}")
    raise

# Session local for database session management
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for your models
Base = declarative_base()

# Import models after the Base is created to avoid circular import issues
# This import will be handled lazily at runtime when the application starts
def import_models():
    from app.models import user, user_preference  # Import models here to avoid circular import
    return user, user_preference

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
