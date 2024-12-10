from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment variables
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create async engine and sessionmaker
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Function to initialize the database by creating tables
async def init_db():
    async with engine.begin() as conn:
        # This creates all the tables defined in the Base metadata
        await conn.run_sync(Base.metadata.create_all)

# New function to create db and tables explicitly (as per your usage in main.py)
async def create_db_and_tables():
    await init_db()
