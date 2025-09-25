from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProfilePreferences(BaseModel):
    theme: str = "light"  # "light" or "dark"
    notifications: bool = True
    auto_save: bool = True

class ProfileSubscription(BaseModel):
    plan: str = "free"  # "free", "pro", or "premium"  
    expires_at: Optional[datetime] = None

class ProfileStats(BaseModel):
    resumes_created: int = 0
    profile_views: int = 0
    downloads_this_month: int = 0
    last_active: datetime = datetime.now()

class ProfileData(BaseModel):
    id: str
    name: str
    title: str
    email: str
    phone: str
    location: str
    linkedin: Optional[str] = None
    website: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    preferences: ProfilePreferences = ProfilePreferences()
    subscription: ProfileSubscription = ProfileSubscription()
    stats: ProfileStats = ProfileStats()
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class ProfileDataCreate(BaseModel):
    name: str
    title: str
    email: str
    phone: str
    location: str
    linkedin: Optional[str] = None
    website: Optional[str] = None
    bio: Optional[str] = None

class ProfileDataUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[ProfilePreferences] = None
