from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..services.chat_service import resume_agent

router = APIRouter()

# Chat request/response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    agent_info: Optional[Dict[str, Any]] = None

@router.get("/resume")
async def get_resume():
    return {"message": "This endpoint will return the user's resume."}

@router.post("/resume")
async def create_resume(resume_data: dict):
    return {"message": "This endpoint will create a new resume.", "data": resume_data}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_user(request: ChatRequest):
    """
    Chat with the LangGraph-powered resume assistant
    """
    try:
        response = await resume_agent.chat(
            message=request.message,
            user_id=request.user_id or "default",
            context=request.context
        )
        
        return ChatResponse(
            response=response,
            user_id=request.user_id or "default"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.get("/chat/info")
async def get_chat_info():
    """
    Get information about the chat agent capabilities
    """
    return resume_agent.get_agent_info()
