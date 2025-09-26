from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class ProfileTable(Base):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)
    linkedin = Column(String, nullable=True)
    website = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Preferences (stored as JSON-like strings for simplicity)
    theme = Column(String, default="light")
    notifications = Column(Boolean, default=True)
    auto_save = Column(Boolean, default=True)
    
    # Subscription
    subscription_plan = Column(String, default="free")
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Stats
    resumes_created = Column(Integer, default=0)
    profile_views = Column(Integer, default=0)
    downloads_this_month = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResumeTable(Base):
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True, index=True)
    profile_id = Column(String, nullable=False)  # Foreign key to profiles
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    location = Column(String, nullable=False)
    linkedin = Column(String, nullable=True)
    website = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)  # JSON string
    skills = Column(Text, nullable=True)  # JSON string  
    education = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatConversationTable(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # References profiles.id
    session_id = Column(String, nullable=False, index=True)
    message_type = Column(String, nullable=False)  # 'human' or 'ai'
    content = Column(Text, nullable=False)
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ResumeVersionTable(Base):
    __tablename__ = "resume_versions"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # References profiles.id
    resume_id = Column(String, nullable=False, index=True)  # References resumes.id
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)  # JSON string of resume content
    changes_summary = Column(Text, nullable=True)
    created_by = Column(String, default="user")  # 'user' or 'ai'
    created_at = Column(DateTime, default=datetime.utcnow)
