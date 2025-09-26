"""
Database migration utilities for resume builder
"""
from sqlalchemy import text
from .connection import engine
import logging

logger = logging.getLogger(__name__)


def create_chat_tables():
    """Create chat conversation and resume version tables"""
    try:
        
        # Create chat_conversations table
        chat_conversations_sql = """
        CREATE TABLE IF NOT EXISTS chat_conversations (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
            user_id VARCHAR NOT NULL,
            session_id VARCHAR NOT NULL,
            message_type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_conversations_session_id ON chat_conversations(session_id);
        CREATE INDEX IF NOT EXISTS idx_chat_conversations_created_at ON chat_conversations(created_at);
        """
        
        # Create resume_versions table
        resume_versions_sql = """
        CREATE TABLE IF NOT EXISTS resume_versions (
            id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
            user_id VARCHAR NOT NULL,
            resume_id VARCHAR NOT NULL,
            version_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            changes_summary TEXT,
            created_by VARCHAR(100) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_resume_versions_user_id ON resume_versions(user_id);
        CREATE INDEX IF NOT EXISTS idx_resume_versions_resume_id ON resume_versions(resume_id);
        """
        
        with engine.connect() as conn:
            conn.execute(text(chat_conversations_sql))
            conn.execute(text(resume_versions_sql))
            conn.commit()
            
        logger.info("Successfully created chat conversation and resume version tables")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create chat tables: {str(e)}")
        return False


def run_migrations():
    """Run all pending migrations"""
    try:
        # Create new tables
        success = create_chat_tables()
        
        if success:
            logger.info("All migrations completed successfully")
        else:
            logger.error("Some migrations failed")
            
        return success
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Run migrations when script is executed directly
    logging.basicConfig(level=logging.INFO)
    run_migrations()
