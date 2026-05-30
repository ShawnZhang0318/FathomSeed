from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user_profile import UserProfile
from app.schemas.profile import UserProfileCreate, UserProfileRead


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=UserProfileRead)
def create_profile(payload: UserProfileCreate, db: Session = Depends(get_db)) -> UserProfile:
    if payload.id:
        existing = db.get(UserProfile, payload.id)
        if existing:
            existing.time_budget_daily = payload.time_budget_daily
            existing.preferred_media = payload.preferred_media
            existing.difficulty_tolerance = payload.difficulty_tolerance
            db.commit()
            db.refresh(existing)
            return existing

    profile_kwargs = {
        "time_budget_daily": payload.time_budget_daily,
        "preferred_media": payload.preferred_media,
        "difficulty_tolerance": payload.difficulty_tolerance,
    }
    if payload.id:
        profile_kwargs["id"] = payload.id
    profile = UserProfile(**profile_kwargs)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/{profile_id}", response_model=UserProfileRead)
def get_profile(profile_id: str, db: Session = Depends(get_db)) -> UserProfile:
    profile = db.get(UserProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
