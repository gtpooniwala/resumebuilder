"""
Change Tracker Service for Resume Editing System
Monitors and logs resume modifications with diff generation
"""
from typing import Dict, Any, List, Optional, Tuple
import json
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import difflib
from ..database.connection import SessionLocal
from ..database.models import ChatConversationTable  # We'll extend the DB schema later
import logging

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of resume changes"""
    PERSONAL_INFO = "personal_info"
    SUMMARY = "summary"
    EXPERIENCE_ADD = "experience_add"
    EXPERIENCE_EDIT = "experience_edit"
    EXPERIENCE_DELETE = "experience_delete"
    SKILLS_ADD = "skills_add"
    SKILLS_EDIT = "skills_edit"
    SKILLS_DELETE = "skills_delete"
    EDUCATION_ADD = "education_add"
    EDUCATION_EDIT = "education_edit"
    EDUCATION_DELETE = "education_delete"
    FORMAT_CHANGE = "format_change"
    OTHER = "other"


@dataclass
class ResumeChange:
    """Represents a single resume change"""
    id: str
    user_id: str
    session_id: Optional[str]
    change_type: ChangeType
    section: str
    field_path: str  # JSON path to the changed field (e.g., "experience.0.description")
    old_value: Any
    new_value: Any
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "change_type": self.change_type.value,
            "section": self.section,
            "field_path": self.field_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class ChangeTracker:
    """
    Tracks and manages resume changes with diff generation capabilities.
    """

    def __init__(self):
        self.max_history_days = 30  # Keep change history for 30 days
        self.max_changes_per_user = 1000  # Limit changes per user
    
    def track_change(
        self, 
        user_id: str,
        old_resume: Dict[str, Any],
        new_resume: Dict[str, Any],
        session_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> List[ResumeChange]:
        """
        Track changes between two resume versions.
        
        Args:
            user_id: User identifier
            old_resume: Previous resume data
            new_resume: New resume data
            session_id: Optional session identifier
            description: Optional change description
            
        Returns:
            List of detected changes
        """
        try:
            changes = self._detect_changes(old_resume, new_resume)
            tracked_changes = []
            
            for change_data in changes:
                change = ResumeChange(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    session_id=session_id,
                    change_type=change_data["type"],
                    section=change_data["section"],
                    field_path=change_data["field_path"],
                    old_value=change_data["old_value"],
                    new_value=change_data["new_value"],
                    description=description or change_data["description"],
                    timestamp=datetime.utcnow(),
                    metadata=change_data.get("metadata")
                )
                
                # Save to database (placeholder - will implement with proper schema)
                self._save_change(change)
                tracked_changes.append(change)
            
            logger.info(f"Tracked {len(tracked_changes)} changes for user {user_id}")
            return tracked_changes
            
        except Exception as e:
            logger.error(f"Failed to track changes: {str(e)}")
            return []
    
    def get_change_history(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        limit: int = 50,
        change_type: Optional[ChangeType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get change history for a user.
        
        Args:
            user_id: User identifier
            session_id: Optional session filter
            limit: Maximum number of changes to return
            change_type: Optional change type filter
            
        Returns:
            List of changes as dictionaries
        """
        try:
            # Placeholder implementation - will implement with proper database schema
            changes = self._load_changes_from_storage(user_id, session_id, limit, change_type)
            return [change.to_dict() for change in changes]
            
        except Exception as e:
            logger.error(f"Failed to get change history: {str(e)}")
            return []
    
    def get_change_diff(self, change_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed diff for a specific change.
        
        Args:
            change_id: Change identifier
            
        Returns:
            Diff information or None if not found
        """
        try:
            change = self._load_change_by_id(change_id)
            if not change:
                return None
            
            # Generate detailed diff
            diff_data = self._generate_diff(change.old_value, change.new_value)
            
            return {
                "change_id": change_id,
                "field_path": change.field_path,
                "section": change.section,
                "change_type": change.change_type.value,
                "timestamp": change.timestamp.isoformat(),
                "diff": diff_data,
                "description": change.description
            }
            
        except Exception as e:
            logger.error(f"Failed to get change diff: {str(e)}")
            return None
    
    def revert_change(self, user_id: str, change_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Revert a specific change.
        
        Args:
            user_id: User identifier
            change_id: Change identifier
            
        Returns:
            Tuple of (success, reverted_data)
        """
        try:
            change = self._load_change_by_id(change_id)
            if not change or change.user_id != user_id:
                return False, None
            
            # Create revert change record
            revert_change = ResumeChange(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=change.session_id,
                change_type=change.change_type,
                section=change.section,
                field_path=change.field_path,
                old_value=change.new_value,  # Reversed
                new_value=change.old_value,  # Reversed
                description=f"Reverted change: {change.description}",
                timestamp=datetime.utcnow(),
                metadata={"reverted_change_id": change_id}
            )
            
            self._save_change(revert_change)
            
            # Return the data to revert to
            revert_data = {
                "field_path": change.field_path,
                "value": change.old_value,
                "section": change.section
            }
            
            logger.info(f"Reverted change {change_id} for user {user_id}")
            return True, revert_data
            
        except Exception as e:
            logger.error(f"Failed to revert change: {str(e)}")
            return False, None
    
    def _detect_changes(self, old_resume: Dict[str, Any], new_resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect changes between two resume versions.
        """
        changes = []
        
        # Check personal info changes
        old_personal = old_resume.get("personalInfo", {})
        new_personal = new_resume.get("personalInfo", {})
        changes.extend(self._detect_dict_changes(old_personal, new_personal, "personalInfo", ChangeType.PERSONAL_INFO))
        
        # Check summary changes
        old_summary = old_resume.get("summary", "")
        new_summary = new_resume.get("summary", "")
        if old_summary != new_summary:
            changes.append({
                "type": ChangeType.SUMMARY,
                "section": "summary",
                "field_path": "summary",
                "old_value": old_summary,
                "new_value": new_summary,
                "description": "Updated professional summary",
                "metadata": {"char_diff": len(new_summary) - len(old_summary)}
            })
        
        # Check experience changes
        old_experience = old_resume.get("experience", [])
        new_experience = new_resume.get("experience", [])
        changes.extend(self._detect_array_changes(old_experience, new_experience, "experience", "Experience"))
        
        # Check skills changes
        old_skills = old_resume.get("skills", {})
        new_skills = new_resume.get("skills", {})
        changes.extend(self._detect_skills_changes(old_skills, new_skills))
        
        # Check education changes
        old_education = old_resume.get("education", [])
        new_education = new_resume.get("education", [])
        changes.extend(self._detect_array_changes(old_education, new_education, "education", "Education"))
        
        return changes
    
    def _detect_dict_changes(self, old_dict: Dict, new_dict: Dict, section: str, change_type: ChangeType) -> List[Dict[str, Any]]:
        """Detect changes in dictionary fields"""
        changes = []
        all_keys = set(old_dict.keys()) | set(new_dict.keys())
        
        for key in all_keys:
            old_value = old_dict.get(key)
            new_value = new_dict.get(key)
            
            if old_value != new_value:
                changes.append({
                    "type": change_type,
                    "section": section,
                    "field_path": f"{section}.{key}",
                    "old_value": old_value,
                    "new_value": new_value,
                    "description": f"Updated {key} in {section}",
                    "metadata": {"field": key}
                })
        
        return changes
    
    def _detect_array_changes(self, old_array: List, new_array: List, section: str, section_name: str) -> List[Dict[str, Any]]:
        """Detect changes in array fields like experience or education"""
        changes = []
        
        # Simple approach: detect length changes and item modifications
        if len(old_array) != len(new_array):
            if len(new_array) > len(old_array):
                # Items added
                for i in range(len(old_array), len(new_array)):
                    changes.append({
                        "type": getattr(ChangeType, f"{section.upper()}_ADD"),
                        "section": section,
                        "field_path": f"{section}.{i}",
                        "old_value": None,
                        "new_value": new_array[i],
                        "description": f"Added new {section_name.lower()} entry",
                        "metadata": {"index": i}
                    })
            else:
                # Items removed
                for i in range(len(new_array), len(old_array)):
                    changes.append({
                        "type": getattr(ChangeType, f"{section.upper()}_DELETE"),
                        "section": section,
                        "field_path": f"{section}.{i}",
                        "old_value": old_array[i],
                        "new_value": None,
                        "description": f"Removed {section_name.lower()} entry",
                        "metadata": {"index": i}
                    })
        
        # Check modifications in existing items
        min_len = min(len(old_array), len(new_array))
        for i in range(min_len):
            if old_array[i] != new_array[i]:
                changes.append({
                    "type": getattr(ChangeType, f"{section.upper()}_EDIT"),
                    "section": section,
                    "field_path": f"{section}.{i}",
                    "old_value": old_array[i],
                    "new_value": new_array[i],
                    "description": f"Modified {section_name.lower()} entry #{i+1}",
                    "metadata": {"index": i}
                })
        
        return changes
    
    def _detect_skills_changes(self, old_skills: Dict, new_skills: Dict) -> List[Dict[str, Any]]:
        """Detect changes in skills section"""
        changes = []
        
        for skill_type in ["technical", "soft"]:
            old_list = old_skills.get(skill_type, [])
            new_list = new_skills.get(skill_type, [])
            
            if old_list != new_list:
                changes.append({
                    "type": ChangeType.SKILLS_EDIT,
                    "section": "skills",
                    "field_path": f"skills.{skill_type}",
                    "old_value": old_list,
                    "new_value": new_list,
                    "description": f"Updated {skill_type} skills",
                    "metadata": {
                        "skill_type": skill_type,
                        "added": list(set(new_list) - set(old_list)),
                        "removed": list(set(old_list) - set(new_list))
                    }
                })
        
        return changes
    
    def _generate_diff(self, old_value: Any, new_value: Any) -> Dict[str, Any]:
        """Generate detailed diff information"""
        if isinstance(old_value, str) and isinstance(new_value, str):
            # Text diff
            diff_lines = list(difflib.unified_diff(
                old_value.splitlines(keepends=True),
                new_value.splitlines(keepends=True),
                fromfile='old',
                tofile='new'
            ))
            
            return {
                "type": "text",
                "old_value": old_value,
                "new_value": new_value,
                "diff_lines": diff_lines,
                "char_diff": len(new_value) - len(old_value)
            }
        else:
            # JSON diff
            return {
                "type": "json",
                "old_value": old_value,
                "new_value": new_value,
                "summary": f"Changed from {type(old_value).__name__} to {type(new_value).__name__}"
            }
    
    def _save_change(self, change: ResumeChange) -> bool:
        """
        Save change to database.
        Placeholder implementation using conversation table for now.
        """
        try:
            with SessionLocal() as db:
                # Store as a special message type for now
                change_record = ChatConversationTable(
                    id=change.id,
                    user_id=change.user_id,
                    session_id=change.session_id or "system",
                    message_type="change_tracking",
                    content=json.dumps(change.to_dict()),
                    message_metadata=json.dumps({
                        "change_type": change.change_type.value,
                        "section": change.section,
                        "field_path": change.field_path
                    }),
                    created_at=change.timestamp
                )
                
                db.add(change_record)
                db.commit()
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to save change: {str(e)}")
            return False
    
    def _load_changes_from_storage(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        limit: int = 50,
        change_type: Optional[ChangeType] = None
    ) -> List[ResumeChange]:
        """Load changes from database storage"""
        try:
            with SessionLocal() as db:
                query = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id,
                    ChatConversationTable.message_type == "change_tracking"
                )
                
                if session_id:
                    query = query.filter(ChatConversationTable.session_id == session_id)
                
                records = query.order_by(
                    ChatConversationTable.created_at.desc()
                ).limit(limit).all()
                
                changes = []
                for record in records:
                    try:
                        change_data = json.loads(record.content)
                        change = ResumeChange(
                            id=change_data["id"],
                            user_id=change_data["user_id"],
                            session_id=change_data.get("session_id"),
                            change_type=ChangeType(change_data["change_type"]),
                            section=change_data["section"],
                            field_path=change_data["field_path"],
                            old_value=change_data["old_value"],
                            new_value=change_data["new_value"],
                            description=change_data["description"],
                            timestamp=datetime.fromisoformat(change_data["timestamp"]),
                            metadata=change_data.get("metadata")
                        )
                        
                        if not change_type or change.change_type == change_type:
                            changes.append(change)
                            
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.warning(f"Failed to parse change record {record.id}: {str(e)}")
                        continue
                
                return changes
                
        except Exception as e:
            logger.error(f"Failed to load changes: {str(e)}")
            return []
    
    def _load_change_by_id(self, change_id: str) -> Optional[ResumeChange]:
        """Load a specific change by ID"""
        try:
            with SessionLocal() as db:
                record = db.query(ChatConversationTable).filter(
                    ChatConversationTable.id == change_id,
                    ChatConversationTable.message_type == "change_tracking"
                ).first()
                
                if not record:
                    return None
                
                change_data = json.loads(record.content)
                return ResumeChange(
                    id=change_data["id"],
                    user_id=change_data["user_id"],
                    session_id=change_data.get("session_id"),
                    change_type=ChangeType(change_data["change_type"]),
                    section=change_data["section"],
                    field_path=change_data["field_path"],
                    old_value=change_data["old_value"],
                    new_value=change_data["new_value"],
                    description=change_data["description"],
                    timestamp=datetime.fromisoformat(change_data["timestamp"]),
                    metadata=change_data.get("metadata")
                )
                
        except Exception as e:
            logger.error(f"Failed to load change by ID: {str(e)}")
            return None
    
    def cleanup_old_changes(self, days_old: int = 30) -> int:
        """Clean up old change records"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            with SessionLocal() as db:
                deleted_count = db.query(ChatConversationTable).filter(
                    ChatConversationTable.message_type == "change_tracking",
                    ChatConversationTable.created_at < cutoff_date
                ).delete()
                
                db.commit()
                
                logger.info(f"Cleaned up {deleted_count} old change records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old changes: {str(e)}")
            return 0


# Global instance
change_tracker = ChangeTracker()
