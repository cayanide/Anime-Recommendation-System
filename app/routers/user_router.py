# app/routers/user_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import models  # This imports all models, including User and UserPreference
from app.models.models import User, UserPreference  # Explicitly import User and UserPreference
from app.models.schemas import PreferenceCreate
from app.auth.security import get_current_user  # Helper function to get authenticated user

router = APIRouter()

# Route to set user preferences (e.g., favorite genres)
@router.post("/preferences")
async def set_preferences(pref: PreferenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Set user preferences such as favorite genres.
    """
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the preference already exists
    existing_pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id, UserPreference.favorite_genre == pref.genre).first()

    if existing_pref:
        raise HTTPException(status_code=400, detail="Preference already exists")

    # Create a new preference
    new_pref = UserPreference(favorite_genre=pref.genre, user_id=current_user.id)
    db.add(new_pref)
    db.commit()
    db.refresh(new_pref)
    return {"msg": "Preference added successfully"}

# Route to get user preferences
@router.get("/preferences")
async def get_preferences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve the user's preferences (e.g., favorite genres).
    """
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).all()

    if not preferences:
        raise HTTPException(status_code=404, detail="No preferences found")

    # Returning a list of genres as a more concise response
    genres = [pref.favorite_genre for pref in preferences]
    return {"preferences": genres}
