from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.schemas import Token, UserAuth
from app.auth.services import create_user, authenticate_user
from app.utils.token import create_access_token

auth_router = APIRouter()

@auth_router.post("/register")
async def register_user(user: UserAuth):
    return await create_user(user)

@auth_router.post("/login", response_model=Token)
async def login_user(user: UserAuth):
    db_user = await authenticate_user(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
