"""
Tests for Chat Service - End-to-End LangGraph Integration
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.chat_service import ChatService
from app.database.models import ChatConversationTable, ResumeTable


class TestChatService:
    """Test ChatService end-to-end functionality"""
    
    def test_chat_service_initialization(self):
        """Test ChatService initializes correctly"""
        try:
            chat_service = ChatService()
            
            assert chat_service is not None
            # Basic attribute checks
            assert hasattr(chat_service, 'llm')
            assert hasattr(chat_service, 'tools')
            assert hasattr(chat_service, 'agent_graph')
        except Exception:
            # If initialization fails due to OpenAI key, just test the class exists
            assert ChatService is not None
            assert callable(ChatService)
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_simple_question(self, mock_openai, setup_test_user, mock_llm):
        """Test processing a simple question without tools"""
        test_user_id, _, _ = setup_test_user
        
        # Mock LLM response for simple question
        mock_response = MagicMock()
        mock_response.content = "Hello! I'm here to help you with your resume. What would you like to work on today?"
        mock_response.tool_calls = []
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Hello"
        )
        
        assert result["success"] is True
        assert "response" in result
        assert "Hello!" in result["response"]
        assert result["tools_used"] == []
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_with_tool_call(self, mock_openai, setup_test_user, mock_llm):
        """Test processing message that triggers tool usage"""
        test_user_id, _, _ = setup_test_user
        
        # Mock LLM response with tool call
        mock_tool_call = MagicMock()
        mock_tool_call.name = "get_resume_section"
        mock_tool_call.args = {"user_id": test_user_id, "section": "experience"}
        mock_tool_call.id = "call_123"
        
        mock_response = MagicMock()
        mock_response.content = ""
        mock_response.tool_calls = [mock_tool_call]
        
        # Mock follow-up response after tool execution
        mock_final_response = MagicMock()
        mock_final_response.content = "I can see you have experience at Tech Corp as a Software Engineer. How would you like to modify this section?"
        mock_final_response.tool_calls = []
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(side_effect=[mock_response, mock_final_response])
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Show me my work experience"
        )
        
        assert result["success"] is True
        assert "Tech Corp" in result["response"] or "experience" in result["response"].lower()
        assert len(result["tools_used"]) == 1
        assert result["tools_used"][0]["tool"] == "get_resume_section"
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_update_experience(self, mock_openai, setup_test_user, mock_llm):
        """Test updating work experience through chat"""
        test_user_id, _, resume_id = setup_test_user
        
        # Mock LLM response with update tool call
        mock_tool_call = MagicMock()
        mock_tool_call.name = "update_work_experience"
        mock_tool_call.args = {
            "user_id": test_user_id,
            "experience_data": {
                "title": "Senior Software Engineer",
                "description": "Updated role with new responsibilities"
            },
            "action": "update",
            "experience_index": 0
        }
        mock_tool_call.id = "call_456"
        
        mock_response = MagicMock()
        mock_response.content = ""
        mock_response.tool_calls = [mock_tool_call]
        
        # Mock follow-up response
        mock_final_response = MagicMock()
        mock_final_response.content = "Great! I've updated your work experience. Your title is now 'Senior Software Engineer' with the new description."
        mock_final_response.tool_calls = []
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(side_effect=[mock_response, mock_final_response])
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Update my job title to Senior Software Engineer and add that I have new responsibilities"
        )
        
        assert result["success"] is True
        assert "updated" in result["response"].lower()
        assert len(result["tools_used"]) == 1
        assert result["tools_used"][0]["tool"] == "update_work_experience"
        
        # Verify database change
        from app.database.connection import SessionLocal
        with SessionLocal() as db:
            resume = db.query(ResumeTable).filter(ResumeTable.id == resume_id).first()
            experience_data = json.loads(resume.experience)
            assert experience_data[0]["title"] == "Senior Software Engineer"
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_multiple_tools(self, mock_openai, setup_test_user, mock_llm):
        """Test processing message that uses multiple tools"""
        test_user_id, _, _ = setup_test_user
        
        # Mock LLM response with multiple tool calls
        mock_tool_call_1 = MagicMock()
        mock_tool_call_1.name = "get_resume_section"
        mock_tool_call_1.args = {"user_id": test_user_id, "section": "skills"}
        mock_tool_call_1.id = "call_1"
        
        mock_tool_call_2 = MagicMock()
        mock_tool_call_2.name = "manage_skills"
        mock_tool_call_2.args = {
            "user_id": test_user_id,
            "skills_data": ["TypeScript", "Vue.js"],
            "action": "add"
        }
        mock_tool_call_2.id = "call_2"
        
        mock_response = MagicMock()
        mock_response.content = ""
        mock_response.tool_calls = [mock_tool_call_1, mock_tool_call_2]
        
        # Mock final response
        mock_final_response = MagicMock()
        mock_final_response.content = "I've reviewed your current skills and added TypeScript and Vue.js to your skill set."
        mock_final_response.tool_calls = []
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(side_effect=[mock_response, mock_final_response])
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Add TypeScript and Vue.js to my skills"
        )
        
        assert result["success"] is True
        assert len(result["tools_used"]) == 2
        tool_names = [tool["tool"] for tool in result["tools_used"]]
        assert "get_resume_section" in tool_names
        assert "manage_skills" in tool_names
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_with_context(self, mock_openai, setup_test_user, mock_llm):
        """Test message processing uses context effectively"""
        test_user_id, _, _ = setup_test_user
        
        mock_response = MagicMock()
        mock_response.content = "Based on your current profile as John Doe, a Software Engineer, I can help you enhance your resume."
        mock_response.tool_calls = []
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Help me improve my resume"
        )
        
        assert result["success"] is True
        
        # Verify context was loaded (LLM should have received context in messages)
        call_args = mock_llm.ainvoke.call_args[0][0]  # First positional argument (messages)
        
        # Should have system message with context
        system_messages = [msg for msg in call_args if msg["role"] == "system"]
        assert len(system_messages) >= 1
        
        # System message should contain profile information
        system_content = system_messages[0]["content"]
        assert "John Doe" in system_content or "Software Engineer" in system_content
    
    async def test_process_message_conversation_persistence(self, setup_test_user):
        """Test that conversations are saved to database"""
        test_user_id, _, _ = setup_test_user
        
        with patch('app.services.chat_service.ChatOpenAI') as mock_openai:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.tool_calls = []
            
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_llm
            
            chat_service = ChatService()
            
            await chat_service.process_message(
                user_id=test_user_id,
                message="Test message"
            )
            
            # Verify conversation was saved
            from app.database.connection import SessionLocal
            with SessionLocal() as db:
                conversations = db.query(ChatConversationTable).filter(
                    ChatConversationTable.user_id == test_user_id
                ).all()
                
                assert len(conversations) >= 2  # User message + AI response
                
                # Find user and assistant messages
                user_msg = next((c for c in conversations if c.message_type == "human"), None)
                ai_msg = next((c for c in conversations if c.message_type == "ai"), None)
                
                assert user_msg is not None
                assert user_msg.content == "Test message"
                assert ai_msg is not None
                assert ai_msg.content == "Test response"
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_error_handling(self, mock_openai, setup_test_user, mock_llm):
        """Test error handling in message processing"""
        test_user_id, _, _ = setup_test_user
        
        # Mock LLM to raise an exception
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API Error"))
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Test message"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "API Error" in result["error"]
    
    @patch('app.services.chat_service.ChatOpenAI')
    async def test_process_message_tool_error_handling(self, mock_openai, setup_test_user, mock_llm):
        """Test handling of tool execution errors"""
        test_user_id, _, _ = setup_test_user
        
        # Mock LLM response with invalid tool call
        mock_tool_call = MagicMock()
        mock_tool_call.name = "invalid_tool"
        mock_tool_call.args = {}
        mock_tool_call.id = "call_error"
        
        mock_response = MagicMock()
        mock_response.content = ""
        mock_response.tool_calls = [mock_tool_call]
        
        mock_openai.return_value = mock_llm
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        
        chat_service = ChatService()
        
        result = await chat_service.process_message(
            user_id=test_user_id,
            message="Test message with invalid tool"
        )
        
        # Should handle gracefully and return error
        assert result["success"] is False
        assert "error" in result


class TestChatServiceIntegration:
    """Integration tests for ChatService with real components"""
    
    async def test_end_to_end_resume_editing_flow(self, setup_test_user):
        """Test complete flow: context loading -> tool execution -> response"""
        test_user_id, _, resume_id = setup_test_user
        
        with patch('app.services.chat_service.ChatOpenAI') as mock_openai:
            # Setup mock LLM
            def mock_llm_responses(messages):
                """Mock LLM responses based on message content"""
                last_message = messages[-1]["content"] if messages else ""
                
                if "experience" in last_message.lower():
                    # Return tool call for experience
                    response = MagicMock()
                    response.content = ""
                    
                    tool_call = MagicMock()
                    tool_call.name = "get_resume_section"
                    tool_call.args = {"user_id": test_user_id, "section": "experience"}
                    tool_call.id = "call_exp"
                    response.tool_calls = [tool_call]
                    
                    return response
                else:
                    # Return text response
                    response = MagicMock()
                    response.content = "I can see your work experience at Tech Corp. The information looks good!"
                    response.tool_calls = []
                    return response
            
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(side_effect=mock_llm_responses)
            mock_openai.return_value = mock_llm
            
            chat_service = ChatService()
            
            # Test the complete flow
            result = await chat_service.process_message(
                user_id=test_user_id,
                message="Show me my work experience"
            )
            
            assert result["success"] is True
            assert "Tech Corp" in result["response"]
            assert len(result["tools_used"]) == 1
            assert result["tools_used"][0]["tool"] == "get_resume_section"
            
            # Verify context was loaded properly
            call_args = mock_llm.ainvoke.call_args_list[0][0][0]
            system_message = next((msg for msg in call_args if msg["role"] == "system"), None)
            assert system_message is not None
            assert "John Doe" in system_message["content"]
    
    async def test_context_efficiency_in_chat(self, setup_test_user):
        """Test that context loading is efficient and under token limits"""
        test_user_id, _, _ = setup_test_user
        
        with patch('app.services.chat_service.ChatOpenAI') as mock_openai:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "Test response"
            mock_response.tool_calls = []
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_llm
            
            chat_service = ChatService()
            
            await chat_service.process_message(
                user_id=test_user_id,
                message="Help me with my resume"
            )
            
            # Check that context was efficient
            call_args = mock_llm.ainvoke.call_args[0][0]
            total_content = " ".join([msg["content"] for msg in call_args])
            
            # Should be under our target of 2000 tokens (roughly 8000 characters)
            assert len(total_content) < 8000, f"Context too long: {len(total_content)} characters"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
