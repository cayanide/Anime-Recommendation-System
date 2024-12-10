# app/auth/services.py
from database.models import User
from database.config import async_session
from passlib.context import CryptContext
from sqlalchemy.future import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user):
    async with async_session() as session:
        async with session.begin():
            db_user = User(username=user["username"], hashed_password=user["password"])
            session.add(db_user)
        await session.commit()
    return {"message": "User registered successfully"}
# Function to authenticate a user
async def authenticate_user(username: str, password: str):
    async with async_session() as session:
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        db_user = result.scalars().first()
        if db_user and pwd_context.verify(password, db_user.hashed_password):
            return db_user
    return None
