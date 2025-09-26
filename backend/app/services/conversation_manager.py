"""
Conversation Manager for Resume Editing System
Handles persistent chat history and context window management
"""
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.connection import SessionLocal
from ..database.models import ChatConversationTable
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation persistence and context window optimization.
    """

    def __init__(self, max_context_length: int = 16000, max_conversation_length: int = 50):
        self.max_context_length = max_context_length
        self.max_conversation_length = max_conversation_length
        self.conversation_summary_threshold = 30  # messages
    
    async def save_message(
        self, 
        user_id: str, 
        message: str, 
        message_type: str, 
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a message to the database.
        
        Args:
            user_id: User identifier
            message: Message content
            message_type: 'human' or 'ai'
            session_id: Optional session identifier
            metadata: Optional additional data
        """
        try:
            if not session_id:
                session_id = self._get_or_create_session_id(user_id)
            
            with SessionLocal() as db:
                conversation = ChatConversationTable(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    session_id=session_id,
                    message_type=message_type,
                    content=message,
                    message_metadata=json.dumps(metadata) if metadata else None,
                    created_at=datetime.utcnow()
                )
                
                db.add(conversation)
                db.commit()
                
                logger.info(f"Saved {message_type} message for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}")
            return False
    
    def get_conversation_context(
        self, 
        user_id: str, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """
        Get conversation history as LangChain messages.
        Handles context window management and compression.
        """
        try:
            with SessionLocal() as db:
                query = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id
                )
                
                if session_id:
                    query = query.filter(ChatConversationTable.session_id == session_id)
                
                # Get recent messages
                messages_data = query.order_by(
                    ChatConversationTable.created_at.desc()
                ).limit(limit or self.max_conversation_length).all()
                
                # Convert to LangChain messages (reverse to chronological order)
                messages = []
                for msg_data in reversed(messages_data):
                    if msg_data.message_type == "human":
                        messages.append(HumanMessage(content=msg_data.content))
                    elif msg_data.message_type == "ai":
                        messages.append(AIMessage(content=msg_data.content))
                
                # Check if context is too long and compress if needed
                if self._estimate_token_count(messages) > self.max_context_length:
                    messages = self._compress_conversation(messages)
                
                logger.info(f"Retrieved {len(messages)} messages for user {user_id}")
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get conversation context: {str(e)}")
            return []
    
    def get_session_id(self, user_id: str) -> str:
        """
        Get or create a session ID for a user.
        Returns existing session if available, otherwise creates a new one.
        """
        try:
            with SessionLocal() as db:
                # Get the most recent message for this user
                recent_message = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id
                ).order_by(ChatConversationTable.created_at.desc()).first()
                
                if recent_message:
                    return recent_message.session_id
                
                # Create new session with UUID to ensure uniqueness
                unique_id = str(uuid.uuid4())[:8]
                new_session_id = f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
                logger.info(f"Created new session {new_session_id} for user {user_id}")
                return new_session_id
                
        except Exception as e:
            logger.error(f"Failed to get session ID: {str(e)}")
            unique_id = str(uuid.uuid4())[:8]
            return f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
    
    def create_new_session(self, user_id: str) -> str:
        """
        Explicitly create a new session for a user.
        Use this when you want to start a fresh conversation.
        """
        try:
            unique_id = str(uuid.uuid4())[:8]
            new_session_id = f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
            logger.info(f"Created new session {new_session_id} for user {user_id}")
            return new_session_id
        except Exception as e:
            logger.error(f"Failed to create new session ID: {str(e)}")
            unique_id = str(uuid.uuid4())[:8]
            return f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{unique_id}"
    
    def _get_or_create_session_id(self, user_id: str) -> str:
        """Helper to get or create session ID"""
        return self.get_session_id(user_id)
    
    def _compress_conversation(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Compress conversation when it exceeds token limits.
        Keep recent messages + summarize older ones.
        """
        try:
            if len(messages) <= 10:
                return messages
            
            # Keep the last 10 messages
            recent_messages = messages[-10:]
            older_messages = messages[:-10]
            
            # Create a summary of older messages
            summary = self._summarize_conversation(older_messages)
            summary_message = AIMessage(
                content=f"[Previous conversation summary: {summary}]"
            )
            
            # Return summary + recent messages
            compressed = [summary_message] + recent_messages
            logger.info(f"Compressed conversation from {len(messages)} to {len(compressed)} messages")
            return compressed
            
        except Exception as e:
            logger.error(f"Failed to compress conversation: {str(e)}")
            return messages[-20:]  # Fallback: just keep last 20 messages
    
    def _summarize_conversation(self, messages: List[BaseMessage]) -> str:
        """
        Create a summary of conversation messages.
        Simple keyword-based summary for now.
        """
        try:
            # Extract key topics and actions from messages
            topics = set()
            actions = set()
            
            for message in messages:
                content = message.content.lower()
                
                # Look for resume sections
                if "experience" in content or "work" in content:
                    topics.add("work experience")
                if "education" in content:
                    topics.add("education")
                if "skills" in content:
                    topics.add("skills")
                if "summary" in content:
                    topics.add("professional summary")
                
                # Look for actions
                if any(word in content for word in ["update", "edit", "change"]):
                    actions.add("editing")
                if any(word in content for word in ["add", "create"]):
                    actions.add("adding content")
                if "help" in content:
                    actions.add("seeking advice")
            
            # Build summary
            summary_parts = []
            if topics:
                summary_parts.append(f"Discussed: {', '.join(topics)}")
            if actions:
                summary_parts.append(f"Actions: {', '.join(actions)}")
            
            if not summary_parts:
                summary_parts.append("General resume consultation")
            
            return "; ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Failed to summarize conversation: {str(e)}")
            return "Previous conversation about resume editing"
    
    def _estimate_token_count(self, messages: List[BaseMessage]) -> int:
        """
        Rough estimation of token count for messages.
        Rule of thumb: 1 token ≈ 4 characters for English text.
        """
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4
    
    def clear_old_conversations(self, days_old: int = 30) -> int:
        """
        Clean up old conversations from database.
        
        Args:
            days_old: Delete conversations older than this many days
            
        Returns:
            Number of conversations deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            with SessionLocal() as db:
                deleted_count = db.query(ChatConversationTable).filter(
                    ChatConversationTable.created_at < cutoff_date
                ).delete()
                
                db.commit()
                
                logger.info(f"Deleted {deleted_count} old conversations")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to clear old conversations: {str(e)}")
            return 0
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user with metadata.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of session data with metadata
        """
        try:
            with SessionLocal() as db:
                # Get session details with message counts and last activity
                session_details = db.query(
                    ChatConversationTable.session_id,
                    func.count(ChatConversationTable.id).label('message_count'),
                    func.min(ChatConversationTable.created_at).label('created_at'),
                    func.max(ChatConversationTable.created_at).label('last_activity'),
                    ChatConversationTable.content.label('first_message_content')
                ).filter(
                    ChatConversationTable.user_id == user_id
                ).group_by(ChatConversationTable.session_id).order_by(
                    func.max(ChatConversationTable.created_at).desc()
                ).limit(limit).all()
                
                sessions = []
                for session in session_details:
                    # Get the first human message for session title
                    first_human_message = db.query(ChatConversationTable).filter(
                        ChatConversationTable.user_id == user_id,
                        ChatConversationTable.session_id == session.session_id,
                        ChatConversationTable.message_type == 'human'
                    ).order_by(ChatConversationTable.created_at.asc()).first()
                    
                    # Create a session title from first message or timestamp
                    if first_human_message:
                        title = first_human_message.content[:50] + ("..." if len(first_human_message.content) > 50 else "")
                    else:
                        title = f"Chat Session {session.created_at.strftime('%m/%d %H:%M')}"
                    
                    sessions.append({
                        "session_id": session.session_id,
                        "title": title,
                        "message_count": session.message_count,
                        "created_at": session.created_at.isoformat(),
                        "last_activity": session.last_activity.isoformat(),
                        "is_active": (datetime.utcnow() - session.last_activity).days < 1
                    })
                
                logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    def get_session_messages(self, user_id: str, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all messages for a specific session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of messages in chronological order
        """
        try:
            with SessionLocal() as db:
                messages = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id,
                    ChatConversationTable.session_id == session_id
                ).order_by(ChatConversationTable.created_at.asc()).limit(limit).all()
                
                return [{
                    "id": msg.id,
                    "type": msg.message_type,
                    "message": msg.content,
                    "timestamp": msg.created_at.isoformat(),
                    "metadata": json.loads(msg.message_metadata) if msg.message_metadata else None
                } for msg in messages]
                
        except Exception as e:
            logger.error(f"Failed to get session messages: {str(e)}")
            return []
    
    def delete_session(self, user_id: str, session_id: str) -> bool:
        """
        Delete a specific chat session and all its messages.
        
        Args:
            user_id: User identifier
            session_id: Session identifier to delete
            
        Returns:
            True if session was deleted successfully
        """
        try:
            with SessionLocal() as db:
                deleted_count = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id,
                    ChatConversationTable.session_id == session_id
                ).delete()
                
                db.commit()
                
                if deleted_count > 0:
                    logger.info(f"Deleted session {session_id} with {deleted_count} messages for user {user_id}")
                    return True
                else:
                    logger.warning(f"No session found to delete: {session_id} for user {user_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            return False
    
    def rename_session(self, user_id: str, session_id: str, new_title: str) -> bool:
        """
        Rename a chat session by updating metadata.
        Note: This would require adding a title field to the database schema.
        For now, this is a placeholder for future implementation.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            new_title: New title for the session
            
        Returns:
            True if session was renamed successfully
        """
        # TODO: Implement when session titles are added to database schema
        logger.info(f"Session rename requested for {session_id}: '{new_title}' (not yet implemented)")
        return False
    
    def get_user_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get conversation statistics for a user.
        """
        try:
            with SessionLocal() as db:
                total_messages = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id
                ).count()
                
                total_sessions = db.query(ChatConversationTable.session_id).filter(
                    ChatConversationTable.user_id == user_id
                ).distinct().count()
                
                recent_messages = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id,
                    ChatConversationTable.created_at > datetime.utcnow() - timedelta(days=7)
                ).count()
                
                last_activity = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == user_id
                ).order_by(ChatConversationTable.created_at.desc()).first()
                
                return {
                    "total_messages": total_messages,
                    "total_sessions": total_sessions,
                    "recent_messages_7days": recent_messages,
                    "last_activity": last_activity.created_at.isoformat() if last_activity else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {str(e)}")
            return {"total_messages": 0, "total_sessions": 0, "recent_messages_7days": 0, "last_activity": None}


# Global instance
conversation_manager = ConversationManager()
