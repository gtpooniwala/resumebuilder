from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ..database.connection import get_db
from ..database.models import ProfileTable
from ..models.profile import ProfileData, ProfileDataCreate, ProfileDataUpdate, ProfilePreferences, ProfileSubscription, ProfileStats

router = APIRouter()

def db_profile_to_pydantic(db_profile: ProfileTable) -> ProfileData:
    """Convert database profile to Pydantic model"""
    return ProfileData(
        id=db_profile.id,
        name=db_profile.name,
        title=db_profile.title,
        email=db_profile.email,
        phone=db_profile.phone,
        location=db_profile.location,
        linkedin=db_profile.linkedin,
        website=db_profile.website,
        avatar=db_profile.avatar,
        bio=db_profile.bio,
        preferences=ProfilePreferences(
            theme=db_profile.theme,
            notifications=db_profile.notifications,
            auto_save=db_profile.auto_save
        ),
        subscription=ProfileSubscription(
            plan=db_profile.subscription_plan,
            expires_at=db_profile.subscription_expires_at
        ),
        stats=ProfileStats(
            resumes_created=db_profile.resumes_created,
            profile_views=db_profile.profile_views,
            downloads_this_month=db_profile.downloads_this_month,
            last_active=db_profile.last_active
        ),
        created_at=db_profile.created_at,
        updated_at=db_profile.updated_at
    )

@router.post("/profiles/", response_model=ProfileData)
def create_profile(profile: ProfileDataCreate, db: Session = Depends(get_db)):
    """Create a new user profile"""
    profile_id = str(uuid.uuid4())
    
    db_profile = ProfileTable(
        id=profile_id,
        name=profile.name,
        title=profile.title,
        email=profile.email,
        phone=profile.phone,
        location=profile.location,
        linkedin=profile.linkedin,
        website=profile.website,
        bio=profile.bio
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile_to_pydantic(db_profile)

@router.get("/profiles/{profile_id}", response_model=ProfileData)
def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a user profile by ID"""
    db_profile = db.query(ProfileTable).filter(ProfileTable.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update last_active timestamp
    db_profile.last_active = datetime.utcnow()
    db.commit()
    
    return db_profile_to_pydantic(db_profile)

@router.get("/profiles/", response_model=List[ProfileData])
def list_profiles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all user profiles"""
    profiles = db.query(ProfileTable).offset(skip).limit(limit).all()
    return [db_profile_to_pydantic(profile) for profile in profiles]

@router.put("/profiles/{profile_id}", response_model=ProfileData)
def update_profile(profile_id: str, profile_update: ProfileDataUpdate, db: Session = Depends(get_db)):
    """Update a user profile"""
    db_profile = db.query(ProfileTable).filter(ProfileTable.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile_update.dict(exclude_unset=True)
    
    # Handle preferences separately
    if "preferences" in update_data:
        prefs = update_data.pop("preferences")
        if "theme" in prefs:
            db_profile.theme = prefs["theme"]
        if "notifications" in prefs:
            db_profile.notifications = prefs["notifications"]
        if "auto_save" in prefs:
            db_profile.auto_save = prefs["auto_save"]
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db_profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_profile)
    
    return db_profile_to_pydantic(db_profile)

@router.delete("/profiles/{profile_id}")
def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Delete a user profile"""
    db_profile = db.query(ProfileTable).filter(ProfileTable.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(db_profile)
    db.commit()
    
    return {"message": "Profile deleted successfully"}

@router.patch("/profiles/{profile_id}/stats")
def update_profile_stats(profile_id: str, db: Session = Depends(get_db)):
    """Update profile view count"""
    db_profile = db.query(ProfileTable).filter(ProfileTable.id == profile_id).first()
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_profile.profile_views += 1
    db_profile.last_active = datetime.utcnow()
    db.commit()
    
    return {"message": "Profile stats updated"}
