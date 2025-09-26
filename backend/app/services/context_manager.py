"""
Context Manager for Resume Editing System
Implements hybrid smart context as per design document
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from ..database.connection import SessionLocal
from ..database.models import ProfileTable, ResumeTable
import json
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context for resume editing conversations.
    Provides base context (resume outline + basic profile) plus dynamic tools.
    """

    def __init__(self):
        self.max_base_context_tokens = 2000  # From design config
    
    def get_base_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get base context for conversation.
        Returns essential info without full content.
        """
        try:
            with SessionLocal() as db:
                context = {
                    "resume_outline": self._get_resume_structure(db, user_id),
                    "profile_basic": self._get_basic_profile(db, user_id),
                    "recent_activity": self._get_recent_changes(db, user_id),
                    "capabilities": self._get_available_tools()
                }
                
                logger.info(f"Generated base context for user {user_id}")
                return context
                
        except Exception as e:
            logger.error(f"Failed to get base context for user {user_id}: {str(e)}")
            return self._get_fallback_context()
    
    def _get_resume_structure(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get resume structure without full content - token efficient.
        """
        try:
            # Get the most recent resume for this user
            resume = db.query(ResumeTable).filter(
                ResumeTable.profile_id == user_id
            ).order_by(ResumeTable.updated_at.desc()).first()
            
            if not resume:
                return {
                    "exists": False,
                    "sections": [],
                    "message": "No resume found - ready to create one"
                }
            
            # Parse JSON fields to count items
            experience_count = 0
            education_count = 0
            skills_count = 0
            
            try:
                if resume.experience:
                    experience_data = json.loads(resume.experience)
                    experience_count = len(experience_data) if isinstance(experience_data, list) else 1
            except:
                pass
                
            try:
                if resume.education:
                    education_data = json.loads(resume.education)
                    education_count = len(education_data) if isinstance(education_data, list) else 1
            except:
                pass
                
            try:
                if resume.skills:
                    skills_data = json.loads(resume.skills)
                    skills_count = len(skills_data) if isinstance(skills_data, list) else 1
            except:
                pass
            
            return {
                "exists": True,
                "resume_id": resume.id,
                "sections": {
                    "contact": bool(resume.email and resume.phone),
                    "summary": bool(resume.summary),
                    "experience": {"count": experience_count, "has_content": experience_count > 0},
                    "education": {"count": education_count, "has_content": education_count > 0},
                    "skills": {"count": skills_count, "has_content": skills_count > 0}
                },
                "last_modified": resume.updated_at.isoformat() if resume.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting resume structure: {str(e)}")
            return {"exists": False, "error": "Could not load resume structure"}
    
    def _get_basic_profile(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get basic profile info - name, title, location only.
        """
        try:
            profile = db.query(ProfileTable).filter(ProfileTable.id == user_id).first()
            
            if not profile:
                return {
                    "exists": False,
                    "message": "No profile found - please create one"
                }
            
            return {
                "exists": True,
                "name": profile.name,
                "title": profile.title,
                "location": profile.location,
                "subscription_plan": profile.subscription_plan
            }
            
        except Exception as e:
            logger.error(f"Error getting basic profile: {str(e)}")
            return {"exists": False, "error": "Could not load profile"}
    
    def _get_recent_changes(self, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get recent activity summary - what was last modified.
        """
        try:
            # For now, just return the last activity from profile
            profile = db.query(ProfileTable).filter(ProfileTable.id == user_id).first()
            
            recent_activity = {
                "last_active": profile.last_active.isoformat() if profile and profile.last_active else None,
                "resumes_created": profile.resumes_created if profile else 0,
                "recent_session": "This is a new conversation"
            }
            
            return recent_activity
            
        except Exception as e:
            logger.error(f"Error getting recent changes: {str(e)}")
            return {"recent_session": "Unable to load recent activity"}
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools for the LLM to use.
        """
        return [
            {
                "name": "get_resume_section",
                "description": "Get detailed content of a specific resume section",
                "parameters": ["section_name"]
            },
            {
                "name": "get_full_profile",
                "description": "Get complete profile information",
                "parameters": ["user_id"]
            },
            {
                "name": "update_work_experience",
                "description": "Add or update work experience entry",
                "parameters": ["experience_data", "action"]
            },
            {
                "name": "edit_professional_summary",
                "description": "Update the professional summary section",
                "parameters": ["new_summary"]
            },
            {
                "name": "manage_skills",
                "description": "Add, remove, or update skills",
                "parameters": ["skills_data", "action"]
            },
            {
                "name": "search_resume_content",
                "description": "Search for specific content in resume",
                "parameters": ["query"]
            }
        ]
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """
        Fallback context when database queries fail.
        """
        return {
            "resume_outline": {"exists": False, "error": "Could not load resume"},
            "profile_basic": {"exists": False, "error": "Could not load profile"},
            "recent_activity": {"recent_session": "Database connection error"},
            "capabilities": self._get_available_tools()
        }
    
    def estimate_context_tokens(self, context: Dict[str, Any]) -> int:
        """
        Rough estimation of token count for context.
        Rule of thumb: 1 token ≈ 4 characters for English text.
        """
        context_str = json.dumps(context)
        return len(context_str) // 4


# Global instance
context_manager = ContextManager()
