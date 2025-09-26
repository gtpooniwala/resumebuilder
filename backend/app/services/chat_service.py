import os
import json
import asyncio
import logging
from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from fastapi import HTTPException

# Import our new services
from .context_manager import context_manager
from .conversation_manager import conversation_manager
from .resume_tools import (
    ResumeEditingTools,
    resume_editing_tools
)

logger = logging.getLogger(__name__)


class SimpleAgentState(TypedDict):
    """Simplified state structure for our LangGraph agent"""
    messages: List[BaseMessage]
    user_id: str
    session_id: Optional[str]


class ResumeAgentService:
    """Simple LangGraph-based resume chatbot service with tools"""
    
    def __init__(self):
        # Initialize OpenAI LLM with tools
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Get available tools
        self.tools = self._get_resume_tools()
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build the simple agent graph
        self.agent_graph = self._build_agent_graph()
    
    def _get_resume_tools(self):
        """Get the list of resume editing tools for the LLM"""
        from .resume_tools import (
            ResumeEditingTools
        )
        
        # Return the actual tool functions
        return [
            ResumeEditingTools.get_resume_section,
            ResumeEditingTools.get_full_profile,
            ResumeEditingTools.update_work_experience,
            ResumeEditingTools.edit_professional_summary,
            ResumeEditingTools.manage_skills,
            ResumeEditingTools.search_resume_content
        ]
    
    def _build_agent_graph(self) -> StateGraph:
        """Build the simple LangGraph agent workflow - just 2 nodes"""
        
        # Create the graph
        workflow = StateGraph(SimpleAgentState)
        
        # Add nodes - simple approach
        workflow.add_node("chatbot_with_tools", self._chatbot_with_tools_node)
        workflow.add_node("respond", self._respond_node)
        
        # Set entry point
        workflow.set_entry_point("chatbot_with_tools")
        
        # Add edges - linear flow
        workflow.add_edge("chatbot_with_tools", "respond")
        workflow.add_edge("respond", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _chatbot_with_tools_node(self, state: SimpleAgentState) -> SimpleAgentState:
        """
        Main chatbot node with tools integration.
        This combines conversation history, context, and tool usage.
        """
        try:
            user_id = state["user_id"]
            current_message = state["messages"][-1].content if state["messages"] else ""
            
            # Get conversation history from database
            conversation_history = conversation_manager.get_conversation_context(
                user_id, 
                state.get("session_id"),
                limit=20  # Keep recent context
            )
            
            # Get base context (resume outline + basic profile)
            base_context = context_manager.get_base_context(user_id)
            
            # Create system prompt with context
            system_prompt = f"""You are a professional resume and career advisor AI assistant.
            
Your role is to help users improve their resumes, provide career advice, and assist with job search strategies.

AVAILABLE TOOLS:
- get_resume_section: Get detailed content of specific resume sections
- get_full_profile: Get complete profile information  
- update_work_experience: Add/update/remove work experience entries
- edit_professional_summary: Update professional summary
- manage_skills: Add/remove/update skills
- search_resume_content: Search for specific content in resume

CURRENT USER CONTEXT:
{json.dumps(base_context, indent=2)}

GUIDELINES:
- Be encouraging and professional
- Use tools when you need specific information or to make changes
- Always confirm changes with the user before applying them
- Ask clarifying questions when needed
- Focus on resume improvement and career development
- Be concise but helpful

Remember: You have access to tools to get detailed information and make changes. Use them when appropriate!"""

            # Prepare messages for LLM
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (but not too much)
            for msg in conversation_history[-10:]:  # Last 10 messages
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": current_message})
            
            # Get LLM response with tools
            response = self.llm_with_tools.invoke(messages)
            
            # Add the AI response to state
            state["messages"].append(AIMessage(content=response.content))
            
            return state
            
        except Exception as e:
            logger.error(f"Error in chatbot node: {str(e)}")
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_msg))
            return state
    
    def _respond_node(self, state: SimpleAgentState) -> SimpleAgentState:
        """Final response node - handles response formatting and saving"""
        try:
            user_id = state["user_id"]
            session_id = state.get("session_id") or conversation_manager.get_session_id(user_id)
            
            # Get the last human and AI messages
            messages = state["messages"]
            if len(messages) >= 2:
                human_message = None
                ai_message = None
                
                # Find the last human and AI messages
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage) and ai_message is None:
                        ai_message = msg
                    elif isinstance(msg, HumanMessage) and human_message is None:
                        human_message = msg
                    
                    if human_message and ai_message:
                        break
                
                # Save messages to database
                if human_message:
                    asyncio.create_task(conversation_manager.save_message(
                        user_id, human_message.content, "human", session_id
                    ))
                
                if ai_message:
                    asyncio.create_task(conversation_manager.save_message(
                        user_id, ai_message.content, "ai", session_id
                    ))
            
            # Update session_id in state
            state["session_id"] = session_id
            
            return state
            
        except Exception as e:
            logger.error(f"Error in respond node: {str(e)}")
            return state
    
    async def chat(self, message: str, user_id: str = "default", context: Optional[Dict[str, Any]] = None) -> str:
        """Main chat interface - simplified"""
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        try:
            # Get or create session
            session_id = conversation_manager.get_session_id(user_id)
            
            # Prepare initial state
            initial_state: SimpleAgentState = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "session_id": session_id
            }
            
            # Run the simple agent graph
            result = self.agent_graph.invoke(initial_state)
            
            # Extract the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                return ai_messages[-1].content
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Chat service error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")
    
    async def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process message and return detailed response for testing"""
        try:
            response = await self.chat(message, user_id)
            
            return {
                "success": True,
                "response": response,
                "tools_used": [],  # Would be populated by actual tool usage
                "user_id": user_id,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Process message error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
                "message": message
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "model": "gpt-4o-mini",
            "framework": "LangGraph (Simple Architecture)",
            "architecture": "2-node workflow with tool integration",
            "capabilities": [
                "Resume advice and career guidance",
                "Real-time resume editing",
                "Professional summary optimization", 
                "Work experience management",
                "Skills management",
                "Resume content search"
            ],
            "tools_available": [
                "get_resume_section",
                "get_full_profile", 
                "update_work_experience",
                "edit_professional_summary",
                "manage_skills",
                "search_resume_content"
            ],
            "features": [
                "Persistent conversation history",
                "Context-aware responses",
                "Hybrid smart context loading",
                "Resume version tracking"
            ]
        }


# Global instance
resume_agent = ResumeAgentService()

# Alias for backward compatibility and testing
ChatService = ResumeAgentService
