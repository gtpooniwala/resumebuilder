import os
from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from fastapi import HTTPException


class AgentState(TypedDict):
    """Define the state structure for our LangGraph agent"""
    messages: List[BaseMessage]
    user_id: str
    context: Dict[str, Any]


class ResumeAgentService:
    """LangGraph-based resume chatbot service"""
    
    def __init__(self):
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0.8,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Build the agent graph
        self.agent_graph = self._build_agent_graph()
    
    def _build_agent_graph(self) -> StateGraph:
        """Build the LangGraph agent workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("chatbot", self._chatbot_node)
        workflow.add_node("respond", self._respond_node)
        
        # Set entry point
        workflow.set_entry_point("chatbot")
        
        # Add edges
        workflow.add_edge("chatbot", "respond")
        workflow.add_edge("respond", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _chatbot_node(self, state: AgentState) -> AgentState:
        """Main chatbot logic node"""
        messages = state["messages"]
        
        # System prompt for resume assistance
        system_prompt = """You are a professional resume and career advisor AI assistant. 
        Your role is to help users improve their resumes, provide career advice, and assist with job search strategies.
        
        You should:
        - Be encouraging and professional
        - Provide specific, actionable advice
        - Ask clarifying questions when needed
        - Focus on resume improvement, career development, and job search
        - Be concise but helpful
        
        Current conversation context: This is a resume building application where users can edit their profiles and resumes."""
        
        # Prepare messages with system prompt
        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "assistant", "content": msg.content})
        
        # Get LLM response
        try:
            response = self.llm.invoke(formatted_messages)
            
            # Add the AI response to messages
            state["messages"].append(AIMessage(content=response.content))
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            state["messages"].append(AIMessage(content=error_msg))
        
        return state
    
    def _respond_node(self, state: AgentState) -> AgentState:
        """Final response formatting node"""
        # This node can be used for post-processing the response
        # For now, it just passes through the state
        return state
    
    async def chat(self, message: str, user_id: str = "default", context: Optional[Dict[str, Any]] = None) -> str:
        """Main chat interface"""
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Prepare initial state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "context": context or {}
        }
        
        try:
            # Run the agent
            result = self.agent_graph.invoke(initial_state)
            
            # Extract the last AI message
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
            if ai_messages:
                return ai_messages[-1].content
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "model": "gpt-4",
            "framework": "LangGraph",
            "capabilities": [
                "Resume advice",
                "Career guidance", 
                "Job search strategies",
                "Professional development"
            ],
            "future_tools": [
                "Resume section editing",
                "Profile management",
                "External data fetching",
                "ATS optimization"
            ]
        }


# Global instance
resume_agent = ResumeAgentService()
