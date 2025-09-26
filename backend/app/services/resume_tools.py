"""
Resume Editing Tools for LangGraph Agent
Implements structured resume modification tools as per design document
"""
from typing import Dict, Any, List, Optional, Union
import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from ..database.connection import SessionLocal
from ..database.models import ResumeTable, ProfileTable, ResumeVersionTable
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)


class ResumeEditingTools:
    """
    Collection of tools for resume editing operations.
    Each tool is designed to be called by the LLM through LangGraph.
    """

    def __init__(self):
        self.version_manager = ResumeVersionManager()
    
    @staticmethod
    @tool
    def get_resume_section(user_id: str, section_name: str) -> Dict[str, Any]:
        """
        Get detailed content of a specific resume section.
        
        Args:
            user_id: User identifier
            section_name: Section to retrieve (contact, summary, experience, education, skills)
        
        Returns:
            Section content with metadata
        """
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(
                    ResumeTable.profile_id == user_id
                ).order_by(ResumeTable.updated_at.desc()).first()
                
                if not resume:
                    return {
                        "success": False,
                        "error": "No resume found for user",
                        "data": None
                    }
                
                section_data = None
                
                if section_name.lower() == "contact":
                    section_data = {
                        "name": resume.name,
                        "title": resume.title,
                        "email": resume.email,
                        "phone": resume.phone,
                        "location": resume.location,
                        "linkedin": resume.linkedin,
                        "website": resume.website
                    }
                elif section_name.lower() == "summary":
                    section_data = resume.summary
                elif section_name.lower() == "experience":
                    section_data = json.loads(resume.experience) if resume.experience else []
                elif section_name.lower() == "education":
                    section_data = json.loads(resume.education) if resume.education else []
                elif section_name.lower() == "skills":
                    section_data = json.loads(resume.skills) if resume.skills else []
                else:
                    return {
                        "success": False,
                        "error": f"Unknown section: {section_name}",
                        "data": None
                    }
                
                return {
                    "success": True,
                    "section": section_name,
                    "data": section_data,
                    "last_modified": resume.updated_at.isoformat() if resume.updated_at else None
                }
                
        except Exception as e:
            logger.error(f"Error getting resume section {section_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    @staticmethod
    @tool
    def get_full_profile(user_id: str) -> Dict[str, Any]:
        """
        Get complete profile information.
        
        Args:
            user_id: User identifier
            
        Returns:
            Complete profile data
        """
        try:
            with SessionLocal() as db:
                profile = db.query(ProfileTable).filter(ProfileTable.id == user_id).first()
                
                if not profile:
                    return {
                        "success": False,
                        "error": "Profile not found",
                        "data": None
                    }
                
                profile_data = {
                    "id": profile.id,
                    "name": profile.name,
                    "title": profile.title,
                    "email": profile.email,
                    "phone": profile.phone,
                    "location": profile.location,
                    "linkedin": profile.linkedin,
                    "website": profile.website,
                    "bio": profile.bio,
                    "subscription_plan": profile.subscription_plan,
                    "resumes_created": profile.resumes_created,
                    "last_active": profile.last_active.isoformat() if profile.last_active else None
                }
                
                return {
                    "success": True,
                    "data": profile_data
                }
                
        except Exception as e:
            logger.error(f"Error getting full profile: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    @staticmethod
    @tool
    def update_work_experience(
        user_id: str, 
        experience_data: Dict[str, Any], 
        action: str = "add",
        experience_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add, update, or remove work experience entry.
        
        Args:
            user_id: User identifier
            experience_data: Work experience information
            action: 'add', 'update', or 'remove'
            experience_index: Index for update/remove operations
            
        Returns:
            Operation result with preview
        """
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(
                    ResumeTable.profile_id == user_id
                ).order_by(ResumeTable.updated_at.desc()).first()
                
                if not resume:
                    return {
                        "success": False,
                        "error": "No resume found. Please create a resume first.",
                        "preview": None
                    }
                
                # Get current experience data
                current_experience = json.loads(resume.experience) if resume.experience else []
                original_experience = current_experience.copy()
                
                # Perform the requested action
                if action.lower() == "add":
                    # Validate required fields
                    required_fields = ["company", "title", "start_date"]
                    for field in required_fields:
                        if field not in experience_data:
                            return {
                                "success": False,
                                "error": f"Missing required field: {field}",
                                "preview": None
                            }
                    
                    # Add new experience
                    new_experience = {
                        "id": str(uuid.uuid4()),
                        "company": experience_data.get("company"),
                        "title": experience_data.get("title"),
                        "start_date": experience_data.get("start_date"),
                        "end_date": experience_data.get("end_date", "Present"),
                        "description": experience_data.get("description", ""),
                        "location": experience_data.get("location", ""),
                        "created_at": datetime.utcnow().isoformat()
                    }
                    current_experience.append(new_experience)
                    
                elif action.lower() == "update":
                    if experience_index is None or experience_index >= len(current_experience):
                        return {
                            "success": False,
                            "error": "Invalid experience index for update",
                            "preview": None
                        }
                    
                    # Update existing experience
                    for key, value in experience_data.items():
                        if key in current_experience[experience_index]:
                            current_experience[experience_index][key] = value
                    
                    current_experience[experience_index]["updated_at"] = datetime.utcnow().isoformat()
                    
                elif action.lower() == "remove":
                    if experience_index is None or experience_index >= len(current_experience):
                        return {
                            "success": False,
                            "error": "Invalid experience index for removal",
                            "preview": None
                        }
                    
                    removed_experience = current_experience.pop(experience_index)
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown action: {action}",
                        "preview": None
                    }
                
                # Create preview
                preview = {
                    "action": action,
                    "before": original_experience,
                    "after": current_experience,
                    "summary": f"{action.title()}d work experience entry"
                }
                
                # Save changes
                resume.experience = json.dumps(current_experience)
                resume.updated_at = datetime.utcnow()
                db.commit()
                
                # Create version backup
                version_manager = ResumeVersionManager()
                version_manager.create_version(user_id, resume.id, "experience", f"Work experience {action}")
                
                return {
                    "success": True,
                    "message": f"Successfully {action}ed work experience",
                    "preview": preview
                }
                
        except Exception as e:
            logger.error(f"Error updating work experience: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "preview": None
            }
    
    @staticmethod
    @tool
    def edit_professional_summary(user_id: str, new_summary: str) -> Dict[str, Any]:
        """
        Update the professional summary section.
        
        Args:
            user_id: User identifier
            new_summary: New summary content
            
        Returns:
            Operation result with preview
        """
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(
                    ResumeTable.profile_id == user_id
                ).order_by(ResumeTable.updated_at.desc()).first()
                
                if not resume:
                    return {
                        "success": False,
                        "error": "No resume found. Please create a resume first.",
                        "preview": None
                    }
                
                old_summary = resume.summary
                
                # Update summary
                resume.summary = new_summary.strip()
                resume.updated_at = datetime.utcnow()
                db.commit()
                
                # Create version backup
                version_manager = ResumeVersionManager()
                version_manager.create_version(user_id, resume.id, "summary", "Professional summary updated")
                
                preview = {
                    "action": "update_summary",
                    "before": old_summary,
                    "after": new_summary,
                    "summary": "Updated professional summary"
                }
                
                return {
                    "success": True,
                    "message": "Successfully updated professional summary",
                    "preview": preview
                }
                
        except Exception as e:
            logger.error(f"Error updating professional summary: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "preview": None
            }
    
    @staticmethod
    @tool
    def manage_skills(
        user_id: str, 
        skills_data: Union[List[str], Dict[str, List[str]]], 
        action: str = "replace"
    ) -> Dict[str, Any]:
        """
        Add, remove, or update skills.
        
        Args:
            user_id: User identifier
            skills_data: Skills information (list of skills or categorized dict)
            action: 'add', 'remove', 'replace'
            
        Returns:
            Operation result with preview
        """
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(
                    ResumeTable.profile_id == user_id
                ).order_by(ResumeTable.updated_at.desc()).first()
                
                if not resume:
                    return {
                        "success": False,
                        "error": "No resume found. Please create a resume first.",
                        "preview": None
                    }
                
                # Get current skills
                current_skills = json.loads(resume.skills) if resume.skills else []
                original_skills = current_skills.copy()
                
                # Handle different skill formats
                if isinstance(skills_data, list):
                    new_skills = skills_data
                elif isinstance(skills_data, dict):
                    # Convert categorized skills to flat list
                    new_skills = []
                    for category, skills_list in skills_data.items():
                        new_skills.extend(skills_list)
                else:
                    return {
                        "success": False,
                        "error": "Invalid skills data format",
                        "preview": None
                    }
                
                # Perform action
                if action.lower() == "add":
                    # Add new skills (avoid duplicates)
                    for skill in new_skills:
                        if skill.strip() and skill.strip() not in current_skills:
                            current_skills.append(skill.strip())
                            
                elif action.lower() == "remove":
                    # Remove specified skills
                    current_skills = [skill for skill in current_skills if skill not in new_skills]
                    
                elif action.lower() == "replace":
                    # Replace all skills
                    current_skills = [skill.strip() for skill in new_skills if skill.strip()]
                    
                else:
                    return {
                        "success": False,
                        "error": f"Unknown action: {action}",
                        "preview": None
                    }
                
                # Update resume
                resume.skills = json.dumps(current_skills)
                resume.updated_at = datetime.utcnow()
                db.commit()
                
                # Create version backup
                version_manager = ResumeVersionManager()
                version_manager.create_version(user_id, resume.id, "skills", f"Skills {action}")
                
                preview = {
                    "action": action,
                    "before": original_skills,
                    "after": current_skills,
                    "summary": f"{action.title()}d skills"
                }
                
                return {
                    "success": True,
                    "message": f"Successfully {action}ed skills",
                    "preview": preview
                }
                
        except Exception as e:
            logger.error(f"Error managing skills: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "preview": None
            }
    
    @staticmethod
    @tool
    def search_resume_content(user_id: str, query: str) -> Dict[str, Any]:
        """
        Search for specific content in resume.
        
        Args:
            user_id: User identifier
            query: Search query
            
        Returns:
            Search results with matches
        """
        try:
            with SessionLocal() as db:
                resume = db.query(ResumeTable).filter(
                    ResumeTable.profile_id == user_id
                ).order_by(ResumeTable.updated_at.desc()).first()
                
                if not resume:
                    return {
                        "success": False,
                        "error": "No resume found",
                        "matches": []
                    }
                
                matches = []
                query_lower = query.lower()
                
                # Search in different sections
                if resume.summary and query_lower in resume.summary.lower():
                    matches.append({
                        "section": "summary",
                        "content": resume.summary,
                        "match_type": "text"
                    })
                
                # Search in experience
                if resume.experience:
                    try:
                        experience_data = json.loads(resume.experience)
                        for i, exp in enumerate(experience_data):
                            if any(query_lower in str(value).lower() for value in exp.values()):
                                matches.append({
                                    "section": "experience",
                                    "index": i,
                                    "content": exp,
                                    "match_type": "experience_entry"
                                })
                    except:
                        pass
                
                # Search in skills
                if resume.skills:
                    try:
                        skills_data = json.loads(resume.skills)
                        matching_skills = [skill for skill in skills_data if query_lower in skill.lower()]
                        if matching_skills:
                            matches.append({
                                "section": "skills",
                                "content": matching_skills,
                                "match_type": "skills"
                            })
                    except:
                        pass
                
                return {
                    "success": True,
                    "query": query,
                    "matches": matches,
                    "total_matches": len(matches)
                }
                
        except Exception as e:
            logger.error(f"Error searching resume content: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "matches": []
            }


class ResumeVersionManager:
    """
    Manages resume versioning and change tracking.
    """
    
    def create_version(
        self, 
        user_id: str, 
        resume_id: str, 
        section_changed: str, 
        change_summary: str
    ) -> bool:
        """
        Create a new version entry for tracking changes.
        """
        try:
            with SessionLocal() as db:
                # Get current resume content
                resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
                if not resume:
                    return False
                
                # Get next version number
                last_version = db.query(ResumeVersionTable).filter(
                    ResumeVersionTable.resume_id == resume_id
                ).order_by(ResumeVersionTable.version_number.desc()).first()
                
                next_version = (last_version.version_number + 1) if last_version else 1
                
                # Create version record
                version = ResumeVersionTable(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    resume_id=resume_id,
                    version_number=next_version,
                    content=json.dumps({
                        "summary": resume.summary,
                        "experience": resume.experience,
                        "education": resume.education,
                        "skills": resume.skills
                    }),
                    changes_summary=f"{section_changed}: {change_summary}",
                    created_by="ai",
                    created_at=datetime.utcnow()
                )
                
                db.add(version)
                db.commit()
                
                logger.info(f"Created version {next_version} for resume {resume_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating resume version: {str(e)}")
            return False


# Global instances
resume_editing_tools = ResumeEditingTools()
resume_version_manager = ResumeVersionManager()
