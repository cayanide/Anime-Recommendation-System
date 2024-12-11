from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ensure all required environment variables are available
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# Check if any of the environment variables are missing
if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("One or more required environment variables are missing.")

# Create SQLAlchemy Database URL using environment variables
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"

# Create an engine instance that connects to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a SessionLocal class to manage database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative model definitions
Base = declarative_base()
