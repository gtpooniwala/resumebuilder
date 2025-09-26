"""
Tests for Conversation Manager - Chat History and Context Window Management
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage, AIMessage

from app.services.conversation_manager import ConversationManager, conversation_manager
from app.database.models import ChatConversationTable
from app.database.connection import SessionLocal


class TestConversationManager:
    """Test Conversation Manager functionality"""
    
    @pytest.mark.asyncio
    async def test_save_message(self, test_user_id, test_session_id):
        """Test saving messages to database"""
        # Save a human message
        success = await conversation_manager.save_message(
            user_id=test_user_id,
            message="Hello, can you help me with my resume?",
            message_type="human",
            session_id=test_session_id,
            metadata={"source": "test"}
        )
        
        assert success is True
        
        # Verify message was saved
        with SessionLocal() as db:
            saved_message = db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id,
                ChatConversationTable.session_id == test_session_id,
                ChatConversationTable.message_type == "human"
            ).first()
            
            assert saved_message is not None
            assert saved_message.content == "Hello, can you help me with my resume?"
            assert saved_message.message_metadata is not None
            
        # Save an AI response
        success = await conversation_manager.save_message(
            user_id=test_user_id,
            message="Of course! I'd be happy to help you improve your resume.",
            message_type="ai",
            session_id=test_session_id
        )
        
        assert success is True
        
        # Cleanup
        with SessionLocal() as db:
            db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).delete()
            db.commit()
    
    def test_get_conversation_context(self, test_user_id, test_session_id):
        """Test retrieving conversation history as LangChain messages"""
        # Create test messages
        with SessionLocal() as db:
            messages = [
                ChatConversationTable(
                    user_id=test_user_id,
                    session_id=test_session_id,
                    message_type="human",
                    content="Hello",
                    created_at=datetime.utcnow() - timedelta(minutes=5)
                ),
                ChatConversationTable(
                    user_id=test_user_id,
                    session_id=test_session_id,
                    message_type="ai", 
                    content="Hi there! How can I help?",
                    created_at=datetime.utcnow() - timedelta(minutes=4)
                ),
                ChatConversationTable(
                    user_id=test_user_id,
                    session_id=test_session_id,
                    message_type="human",
                    content="I need help with my resume",
                    created_at=datetime.utcnow() - timedelta(minutes=3)
                )
            ]
            
            for msg in messages:
                db.add(msg)
            db.commit()
        
        # Get conversation context
        context_messages = conversation_manager.get_conversation_context(
            user_id=test_user_id,
            session_id=test_session_id
        )
        
        # Verify message types and order
        assert len(context_messages) == 3
        assert isinstance(context_messages[0], HumanMessage)
        assert context_messages[0].content == "Hello"
        assert isinstance(context_messages[1], AIMessage)
        assert context_messages[1].content == "Hi there! How can I help?"
        assert isinstance(context_messages[2], HumanMessage)
        assert context_messages[2].content == "I need help with my resume"
        
        # Cleanup
        with SessionLocal() as db:
            db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).delete()
            db.commit()
    
    def test_session_management(self, test_user_id):
        """Test session creation and persistence"""
        # Get new session (should create one since no messages exist)
        session_id_1 = conversation_manager.get_session_id(test_user_id)
        assert session_id_1 is not None
        assert test_user_id in session_id_1
        
        # Save a message to establish session
        with SessionLocal() as db:
            message = ChatConversationTable(
                user_id=test_user_id,
                session_id=session_id_1,
                message_type="human",
                content="Test message",
                created_at=datetime.utcnow()
            )
            db.add(message)
            db.commit()
        
        # Get session again (should return same session)
        session_id_2 = conversation_manager.get_session_id(test_user_id)
        assert session_id_1 == session_id_2
        
        # Explicitly create a new session
        session_id_3 = conversation_manager.create_new_session(test_user_id)
        assert session_id_3 != session_id_1
        assert test_user_id in session_id_3
        
        # Cleanup
        with SessionLocal() as db:
            db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).delete()
            db.commit()
    
    def test_conversation_compression(self, test_user_id):
        """Test conversation compression when context gets too long"""
        # Create many messages to trigger compression
        messages = []
        for i in range(25):  # More than the compression threshold
            messages.append(HumanMessage(content=f"Human message {i}"))
            messages.append(AIMessage(content=f"AI response {i}"))
        
        # Test compression
        compressed = conversation_manager._compress_conversation(messages)
        
        # Should be compressed to summary + recent messages
        assert len(compressed) < len(messages)
        assert len(compressed) <= 11  # Summary + 10 recent messages
        
        # First message should be summary
        assert isinstance(compressed[0], AIMessage)
        assert "Previous conversation summary" in compressed[0].content
        
        # Last messages should be preserved
        assert compressed[-1].content == "AI response 24"
        assert compressed[-2].content == "Human message 24"
    
    def test_conversation_summarization(self, test_user_id):
        """Test conversation summarization logic"""
        messages = [
            HumanMessage(content="I need help updating my work experience"),
            AIMessage(content="I can help you update your work experience section"),
            HumanMessage(content="Add my new job at Google as Software Engineer"),
            AIMessage(content="I'll add that work experience for you"),
            HumanMessage(content="Also update my skills to include Python and React"),
            AIMessage(content="I'll add those skills to your resume")
        ]
        
        summary = conversation_manager._summarize_conversation(messages)
        
        # Should identify key topics and actions
        assert isinstance(summary, str)
        assert len(summary) > 0
        
        # Should contain relevant keywords
        summary_lower = summary.lower()
        # At least some resume-related content should be identified
        assert any(keyword in summary_lower for keyword in [
            "work", "experience", "skills", "editing", "adding"
        ])
    
    def test_token_estimation(self):
        """Test token count estimation"""
        messages = [
            HumanMessage(content="Short message"),
            AIMessage(content="This is a longer message with more content to test token estimation"),
            HumanMessage(content="Another message of medium length for testing")
        ]
        
        token_count = conversation_manager._estimate_token_count(messages)
        
        assert isinstance(token_count, int)
        assert token_count > 0
        # Should be reasonable estimate (roughly 1 token per 4 characters)
        total_chars = sum(len(msg.content) for msg in messages)
        expected_tokens = total_chars // 4
        assert abs(token_count - expected_tokens) < 10  # Allow some variance
    
    def test_clear_old_conversations(self, test_user_id):
        """Test cleanup of old conversations"""
        # Create old and new messages
        with SessionLocal() as db:
            old_message = ChatConversationTable(
                user_id=test_user_id,
                session_id="old-session",
                message_type="human",
                content="Old message",
                created_at=datetime.utcnow() - timedelta(days=31)
            )
            new_message = ChatConversationTable(
                user_id=test_user_id,
                session_id="new-session", 
                message_type="human",
                content="New message",
                created_at=datetime.utcnow()
            )
            db.add(old_message)
            db.add(new_message)
            db.commit()
        
        # Clear old conversations
        deleted_count = conversation_manager.clear_old_conversations(days_old=30)
        
        assert deleted_count >= 1
        
        # Verify old message is gone, new message remains
        with SessionLocal() as db:
            remaining_messages = db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).all()
            
            assert len(remaining_messages) == 1
            assert remaining_messages[0].content == "New message"
        
        # Cleanup
        with SessionLocal() as db:
            db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).delete()
            db.commit()
    
    def test_conversation_stats(self, test_user_id):
        """Test conversation statistics"""
        # Create test messages
        with SessionLocal() as db:
            messages = [
                ChatConversationTable(
                    user_id=test_user_id,
                    session_id="test-session",
                    message_type="human",
                    content="Message 1",
                    created_at=datetime.utcnow() - timedelta(days=8)  # Outside 7 days
                ),
                ChatConversationTable(
                    user_id=test_user_id,
                    session_id="test-session",
                    message_type="ai",
                    content="Response 1", 
                    created_at=datetime.utcnow() - timedelta(hours=1)  # Within 7 days
                )
            ]
            for msg in messages:
                db.add(msg)
            db.commit()
        
        # Get stats
        stats = conversation_manager.get_user_conversation_stats(test_user_id)
        
        assert stats["total_messages"] == 2
        assert stats["recent_messages_7days"] == 1  # Only one in last 7 days
        assert stats["last_activity"] is not None
        
        # Cleanup
        with SessionLocal() as db:
            db.query(ChatConversationTable).filter(
                ChatConversationTable.user_id == test_user_id
            ).delete()
            db.commit()


class TestConversationManagerConfig:
    """Test Conversation Manager configuration"""
    
    def test_initialization(self):
        """Test conversation manager initialization with custom config"""
        custom_manager = ConversationManager(
            max_context_length=8000,
            max_conversation_length=30
        )
        
        assert custom_manager.max_context_length == 8000
        assert custom_manager.max_conversation_length == 30
        assert custom_manager.conversation_summary_threshold == 30
    
    def test_default_configuration(self):
        """Test default configuration values"""
        assert conversation_manager.max_context_length == 16000
        assert conversation_manager.max_conversation_length == 50
        assert conversation_manager.conversation_summary_threshold == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
