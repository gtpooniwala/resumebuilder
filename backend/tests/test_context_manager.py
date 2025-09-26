"""
Tests for Context Manager - Hybrid Smart Context Loading
"""
import pytest
import json
from unittest.mock import Mock, patch

from app.services.context_manager import ContextManager, context_manager
from tests.conftest import assert_database_change


class TestContextManager:
    """Test Context Manager functionality"""
    
    def test_get_base_context_with_existing_user(self, setup_test_user):
        """Test getting base context for existing user with resume"""
        test_user_id, profile_id, resume_id = setup_test_user
        
        # Test getting base context
        context = context_manager.get_base_context(test_user_id)
        
        # Verify context structure
        assert "resume_outline" in context
        assert "profile_basic" in context
        assert "recent_activity" in context
        assert "capabilities" in context
        
        # Verify resume outline
        resume_outline = context["resume_outline"]
        assert resume_outline["exists"] is True
        assert resume_outline["resume_id"] == resume_id
        assert "sections" in resume_outline
        
        # Verify sections detection
        sections = resume_outline["sections"]
        assert sections["contact"] is True  # Has email and phone
        assert sections["summary"]["has_content"] is True
        assert sections["experience"]["count"] == 1
        assert sections["education"]["count"] == 1
        assert sections["skills"]["count"] == 5
        
        # Verify profile basic info
        profile_basic = context["profile_basic"]
        assert profile_basic["exists"] is True
        assert profile_basic["name"] == "John Doe"
        assert profile_basic["title"] == "Software Engineer"
        assert profile_basic["location"] == "San Francisco, CA"
        
        # Verify capabilities list
        capabilities = context["capabilities"]
        assert len(capabilities) == 6
        tool_names = [tool["name"] for tool in capabilities]
        assert "get_resume_section" in tool_names
        assert "update_work_experience" in tool_names
        assert "manage_skills" in tool_names
    
    def test_get_base_context_no_user(self):
        """Test getting context for non-existent user"""
        context = context_manager.get_base_context("non-existent-user")
        
        # Should return fallback context
        assert context["resume_outline"]["exists"] is False
        assert context["profile_basic"]["exists"] is False
        assert "capabilities" in context
        assert len(context["capabilities"]) == 6
    
    def test_estimate_context_tokens(self, setup_test_user):
        """Test token estimation for context"""
        test_user_id, _, _ = setup_test_user
        
        context = context_manager.get_base_context(test_user_id)
        token_count = context_manager.estimate_context_tokens(context)
        
        # Should be reasonable token count (under our 2000 base limit)
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 2000  # Should be under our base context limit
        
        print(f"Estimated tokens for base context: {token_count}")
    
    def test_get_resume_structure_parsing(self, setup_test_user):
        """Test parsing of JSON fields in resume structure"""
        test_user_id, _, _ = setup_test_user
        
        context = context_manager.get_base_context(test_user_id)
        resume_outline = context["resume_outline"]
        
        # Verify JSON parsing worked correctly
        assert resume_outline["sections"]["experience"]["count"] == 1
        assert resume_outline["sections"]["education"]["count"] == 1
        assert resume_outline["sections"]["skills"]["count"] == 5
        
        # Verify has_content flags
        assert resume_outline["sections"]["experience"]["has_content"] is True
        assert resume_outline["sections"]["education"]["has_content"] is True
        assert resume_outline["sections"]["skills"]["has_content"] is True
    
    @patch('app.services.context_manager.SessionLocal')
    def test_database_error_handling(self, mock_session_local):
        """Test error handling when database is unavailable"""
        # Mock database error
        mock_session_local.side_effect = Exception("Database connection failed")
        
        context = context_manager.get_base_context("test-user")
        
        # Should return fallback context
        assert "error" in context["resume_outline"]
        assert "error" in context["profile_basic"]
        assert "capabilities" in context  # Should still have capabilities
    
    def test_context_manager_singleton(self):
        """Test that context_manager is properly initialized"""
        assert isinstance(context_manager, ContextManager)
        assert context_manager.max_base_context_tokens == 2000
        
        # Test multiple calls return consistent results
        capabilities1 = context_manager._get_available_tools()
        capabilities2 = context_manager._get_available_tools()
        assert len(capabilities1) == len(capabilities2)
        assert capabilities1 == capabilities2


class TestContextManagerPerformance:
    """Test Context Manager performance characteristics"""
    
    def test_context_loading_speed(self, setup_test_user):
        """Test that context loading is reasonably fast"""
        import time
        
        test_user_id, _, _ = setup_test_user
        
        start_time = time.time()
        context = context_manager.get_base_context(test_user_id)
        end_time = time.time()
        
        loading_time = end_time - start_time
        print(f"Context loading time: {loading_time:.3f} seconds")
        
        # Should load in under 100ms for local database
        assert loading_time < 0.1, f"Context loading too slow: {loading_time:.3f}s"
        assert context is not None
    
    def test_token_efficiency(self, setup_test_user):
        """Test that hybrid context is token-efficient"""
        test_user_id, _, _ = setup_test_user
        
        # Get base context (hybrid approach)
        base_context = context_manager.get_base_context(test_user_id)
        base_tokens = context_manager.estimate_context_tokens(base_context)
        
        # Simulate full context (what we would send without hybrid approach)
        from app.services.resume_tools import ResumeEditingTools
        full_resume = ResumeEditingTools.get_resume_section(test_user_id, "experience")
        full_profile = ResumeEditingTools.get_full_profile(test_user_id)
        
        full_context = {
            "full_resume": full_resume,
            "full_profile": full_profile,
            "base_context": base_context
        }
        full_tokens = context_manager.estimate_context_tokens(full_context)
        
        print(f"Base context tokens: {base_tokens}")
        print(f"Full context tokens: {full_tokens}")
        
        # Hybrid approach should use significantly fewer tokens
        token_reduction = (full_tokens - base_tokens) / full_tokens
        assert token_reduction > 0.5, f"Token reduction not significant: {token_reduction:.2%}"
        
        print(f"Token reduction: {token_reduction:.2%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
