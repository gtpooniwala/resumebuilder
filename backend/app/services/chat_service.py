import os
import json
import asyncio
import logging
import time
from typing import Dict, List, Any, TypedDict, Optional
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from fastapi import HTTPException

# Import our new services

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
            model="gpt-5",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Get available tools
        self.tools = self._get_resume_tools()
        logger.info(f"Loaded {len(self.tools)} tools: {[tool.name for tool in self.tools]}")
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        logger.info("Successfully bound tools to LLM")
        
        # Build the simple agent graph
        self.agent_graph = self._build_agent_graph()
    
    def _get_resume_tools(self):
        """Get the list of resume editing tools for the LLM"""
        
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
            

            
            # Create system prompt with clear tool usage instructions
            system_prompt = f"""You are a professional resume and career advisor AI assistant that TAKES ACTION.

CRITICAL: You are an ACTIVE assistant that makes changes, not just suggestions. When users ask for improvements or changes with specific direction, you MUST IMPLEMENT them using the editing tools. DO NOT just show them what it would look like - actually update their resume using edit_professional_summary, update_work_experience, or manage_skills.

AVAILABLE TOOLS:
- get_full_profile: Get complete user profile and resume data
- get_resume_section: Get specific sections (contact, summary, experience, education, skills)
- search_resume_content: Search through resume content
- edit_professional_summary: Update professional summary (USE THIS to make changes)
- update_work_experience: Add/edit/remove work experience (USE THIS to make changes)
- manage_skills: Add/edit/remove skills (USE THIS to make changes)

BEHAVIOR RULES:
1. When user asks about their data → Use get_full_profile or get_resume_section
2. When user asks for improvements/changes → 
   a. GET current data first
   b. If the request specifies WHAT to focus on or change → MAKE the changes immediately using editing tools
   c. If the request is completely generic (like "improve my summary" with no direction) → ASK for clarifications 
   d. After making changes → Give a brief confirmation of what you changed
3. Ask for clarifications when you need:
   - Specific content for updates (e.g., "what should the new job title be?")
   - Which item to modify when multiple exist (e.g., "which job should I update?")
   - Context or details for improvements (e.g., "what aspects should I emphasize?")
4. DO NOT ask for clarifications when the request specifies what to focus on or change
5. If the user gives ANY direction about what to emphasize/change, that's enough information to act
6. After getting clarifications, immediately make the requested changes

EXAMPLES OF CORRECT BEHAVIOR:

CLEAR REQUESTS (Act immediately using tools):
- User: "Add Python to my skills" → Call manage_skills to add Python, then say "Added Python to your skills"
- User: "Remove my second job" → Call update_work_experience to remove it, then confirm
- User: "Update my professional summary to highlight my leadership experience" → Get current summary, call edit_professional_summary with improved version, then say "Updated your summary to highlight leadership"
- User: "Update my professional summary to focus more on my React experience" → Get current summary, call edit_professional_summary with React-focused version, then say "Updated your summary to emphasize React experience"

REQUESTS NEEDING CLARIFICATION (Ask first):
- User: "Update my job title" → Ask "Which job title should I update? You have positions at [company names]"
- User: "Add a new skill" → Ask "What skill would you like me to add?"
- User: "Improve my summary" (generic) → Ask "What aspects would you like me to emphasize?"
- User: "Update my work experience" → Ask "Which position should I update and what changes should I make?"

REQUESTS WITH ENOUGH INFO (Act immediately):
- User: "Update my professional summary to focus more on my React experience" → Has clear direction, make the change
- User: "Improve my summary to highlight leadership" → Has clear focus, make the change
- User: "Make my summary more technical" → Has clear direction, make the change

WRONG BEHAVIOR (DO NOT DO THIS):
- Offering multiple pre-written options like "Here are 3 versions, pick one"
- Making changes without enough information
- Asking for clarifications when the request is already clear

You are helping user: {user_id}

BE PROACTIVE: Don't just give advice - take action and make the changes they want."""

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
            logger.info(f"Sending {len(messages)} messages to LLM with tools")
            response = self.llm_with_tools.invoke(messages)
            logger.info(f"LLM response type: {type(response)}")
            logger.info(f"LLM response has tool_calls: {hasattr(response, 'tool_calls')}")
            if hasattr(response, 'tool_calls'):
                logger.info(f"Number of tool calls: {len(response.tool_calls) if response.tool_calls else 0}")
            
            # Handle tool calls if present
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"🔧 LLM TOOL ACTIVITY: Made {len(response.tool_calls)} tool calls")
                for i, tool_call in enumerate(response.tool_calls):
                    logger.info(f"🔧 Tool {i+1}: {tool_call['name']} with args: {tool_call.get('args', {})}")
                
                # Add the LLM response with tool calls to messages
                state["messages"].append(response)
                
                # Execute each tool call
                tool_results_summary = []
                for i, tool_call in enumerate(response.tool_calls):
                    try:
                        logger.info(f"🔧 EXECUTING Tool {i+1}/{len(response.tool_calls)}: {tool_call['name']}")
                        # Execute the tool call
                        tool_result = self._execute_tool_call(tool_call, user_id)
                        
                        # Log detailed results
                        result_preview = json.dumps(tool_result)[:300] if tool_result else "None"
                        logger.info(f"✅ Tool {tool_call['name']} SUCCESS: {result_preview}...")
                        tool_results_summary.append(f"{tool_call['name']}: SUCCESS")
                        
                        # Add tool result to messages
                        tool_message = ToolMessage(
                            content=json.dumps(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                        state["messages"].append(tool_message)
                        
                    except Exception as e:
                        logger.error(f"❌ Tool {tool_call['name']} FAILED: {str(e)}")
                        tool_results_summary.append(f"{tool_call['name']}: FAILED - {str(e)}")
                        error_result = {"error": f"Tool execution failed: {str(e)}"}
                        tool_message = ToolMessage(
                            content=json.dumps(error_result),
                            tool_call_id=tool_call["id"]
                        )
                        state["messages"].append(tool_message)
                
                # Log overall tool execution summary
                logger.info(f"🔧 TOOL EXECUTION SUMMARY: {'; '.join(tool_results_summary)}")
                
                # Log tool usage patterns for monitoring
                tool_names = [tc['name'] for tc in response.tool_calls]
                logger.info(f"📈 TOOL USAGE PATTERN: {' → '.join(tool_names)}")
                
                if any("edit_" in name or "update_" in name or "manage_" in name for name in tool_names):
                    logger.info(f"✏️  DATA MODIFICATION DETECTED: User {user_id} made changes via tools")
                
                # Get final response from LLM after tool execution
                logger.info("Getting final response from LLM after tool execution")
                
                # Create a new message sequence for the final response
                final_messages = [
                    {"role": "system", "content": "Based on the tool results above, provide a helpful response to the user's request. Be specific and actionable."},
                ] + [
                    {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                    for msg in state["messages"][-10:] if isinstance(msg, (HumanMessage, AIMessage)) and msg.content
                ] + [
                    {"role": "system", "content": f"Tool results: {state['messages'][-1].content if state['messages'] else 'No tool results'}"}
                ]
                
                final_response = self.llm.invoke(final_messages)  # Use LLM without tools for final response
                logger.info(f"Final response content length: {len(final_response.content) if final_response.content else 0}")
                state["messages"].append(AIMessage(content=final_response.content))
            else:
                # No tool calls - add response directly
                logger.warning(f"⚠️  NO TOOLS CALLED - LLM responded without using tools: {response.content[:100]}...")
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
    
    def _execute_tool_call(self, tool_call: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        try:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            logger.info(f"🔧 TOOL EXECUTION: {tool_name}")
            logger.info(f"🔧 TOOL ARGS: {json.dumps(tool_args, indent=2)}")
            logger.info(f"🔧 USER_ID: {user_id}")
            
            start_time = time.time()
            
            # Map tool names to actual functions and invoke them properly
            result = None
            if tool_name == "get_resume_section":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.get_resume_section.invoke({
                    "user_id": user_id,
                    "section_name": tool_args.get("section_name", "")
                })
            
            elif tool_name == "get_full_profile":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.get_full_profile.invoke({
                    "user_id": user_id
                })
                
            elif tool_name == "edit_professional_summary":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.edit_professional_summary.invoke({
                    "user_id": user_id,
                    "new_summary": tool_args.get("new_summary", "")
                })
                
            elif tool_name == "update_work_experience":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.update_work_experience.invoke({
                    "user_id": user_id,
                    "experience_data": tool_args.get("experience_data", {}),
                    "action": tool_args.get("action", "add")
                })
                
            elif tool_name == "manage_skills":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.manage_skills.invoke({
                    "user_id": user_id,
                    "skills_data": tool_args.get("skills_data", {}),
                    "action": tool_args.get("action", "add")
                })
                
            elif tool_name == "search_resume_content":
                from .resume_tools import ResumeEditingTools
                result = ResumeEditingTools.search_resume_content.invoke({
                    "user_id": user_id,
                    "query": tool_args.get("query", "")
                })
            
            else:
                execution_time = time.time() - start_time
                logger.error(f"❌ UNKNOWN TOOL: {tool_name} (took {execution_time:.2f}s)")
                return {"error": f"Unknown tool: {tool_name}"}
            
            # Log execution results
            execution_time = time.time() - start_time
            result_dict = result if isinstance(result, dict) else {"result": str(result)}
            
            # Log detailed execution info
            logger.info(f"⏱️  TOOL TIMING: {tool_name} executed in {execution_time:.2f}s")
            logger.info(f"📊 TOOL RESULT TYPE: {type(result).__name__}")
            logger.info(f"📊 TOOL RESULT SIZE: {len(str(result))} characters")
            if isinstance(result, dict) and "error" in result:
                logger.error(f"❌ TOOL RETURNED ERROR: {result['error']}")
            else:
                logger.info(f"✅ TOOL SUCCESS: {tool_name}")
                
            return result_dict
                
        except Exception as e:
            logger.error(f"Tool execution error for {tool_call.get('name', 'unknown')}: {str(e)}")
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def chat(self, message: str, user_id: str = "default", session_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Main chat interface - simplified"""
        if not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        try:
            # Use provided session_id or get/create one
            if not session_id:
                session_id = conversation_manager.get_session_id(user_id)
            
            # Prepare initial state
            initial_state: SimpleAgentState = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "session_id": session_id
            }
            
            # Run the simple agent graph
            result = self.agent_graph.invoke(initial_state)
            
            # Extract the last AI message with content
            ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage) and msg.content.strip()]
            if ai_messages:
                return ai_messages[-1].content
            else:
                # If no AI message with content, check if we have any AI messages and return debug info
                all_ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
                if all_ai_messages:
                    logger.warning(f"Found {len(all_ai_messages)} AI messages but no content")
                    return "I processed your request but encountered an issue generating the response. Please try again."
                else:
                    logger.warning("No AI messages found in result")
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
            "model": "gpt-5",
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
