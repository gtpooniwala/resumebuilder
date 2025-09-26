from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from ..services.chat_service import resume_agent
from ..services.conversation_manager import conversation_manager
from ..services.change_tracker import change_tracker, ChangeType

router = APIRouter()

# Chat request/response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "default"
    session_id: Optional[str] = None
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
            session_id=request.session_id,
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


# Session Management Models
class SessionResponse(BaseModel):
    session_id: str
    title: str
    message_count: int
    created_at: str
    last_activity: str
    is_active: bool

class CreateSessionRequest(BaseModel):
    user_id: str

class CreateSessionResponse(BaseModel):
    session_id: str
    user_id: str
    message: str

class MessageResponse(BaseModel):
    id: str
    type: str
    message: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


# Session Management Endpoints
@router.get("/chat/sessions", response_model=List[SessionResponse])
async def get_user_sessions(user_id: str, limit: int = 50):
    """
    Get all chat sessions for a user
    """
    try:
        sessions = conversation_manager.get_user_sessions(user_id, limit)
        return [SessionResponse(**session) for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")


@router.post("/chat/sessions", response_model=CreateSessionResponse)
async def create_new_session(request: CreateSessionRequest):
    """
    Create a new chat session for a user
    """
    try:
        session_id = conversation_manager.create_new_session(request.user_id)
        return CreateSessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            message="New chat session created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/chat/sessions/{session_id}", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, user_id: str, limit: int = 100):
    """
    Get all messages for a specific session
    """
    try:
        messages = conversation_manager.get_session_messages(user_id, session_id, limit)
        return [MessageResponse(**message) for message in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session messages: {str(e)}")


@router.delete("/chat/sessions/{session_id}")
async def delete_session(session_id: str, user_id: str):
    """
    Delete a specific chat session and all its messages
    """
    try:
        success = conversation_manager.delete_session(user_id, session_id)
        if success:
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.get("/chat/stats")
async def get_chat_stats(user_id: str):
    """
    Get conversation statistics for a user
    """
    try:
        stats = conversation_manager.get_user_conversation_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat stats: {str(e)}")


# Change Tracking Models
class TrackChangeRequest(BaseModel):
    user_id: str
    old_resume: Dict[str, Any]
    new_resume: Dict[str, Any]
    session_id: Optional[str] = None
    description: Optional[str] = None

class RevertChangeRequest(BaseModel):
    user_id: str
    change_id: str


# Change Tracking Endpoints
@router.post("/changes/track")
async def track_resume_changes(request: TrackChangeRequest):
    """
    Track changes between two resume versions
    """
    try:
        changes = change_tracker.track_change(
            user_id=request.user_id,
            old_resume=request.old_resume,
            new_resume=request.new_resume,
            session_id=request.session_id,
            description=request.description
        )
        
        return {
            "message": f"Tracked {len(changes)} changes",
            "changes": [change.to_dict() for change in changes]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track changes: {str(e)}")


@router.get("/changes/history")
async def get_change_history(
    user_id: str, 
    session_id: Optional[str] = None, 
    limit: int = 50,
    change_type: Optional[str] = None
):
    """
    Get change history for a user
    """
    try:
        # Convert change_type string to enum if provided
        change_type_enum = None
        if change_type:
            try:
                change_type_enum = ChangeType(change_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid change_type: {change_type}")
        
        changes = change_tracker.get_change_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit,
            change_type=change_type_enum
        )
        
        return {"changes": changes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get change history: {str(e)}")


@router.get("/changes/diff/{change_id}")
async def get_change_diff(change_id: str):
    """
    Get detailed diff for a specific change
    """
    try:
        diff_data = change_tracker.get_change_diff(change_id)
        if not diff_data:
            raise HTTPException(status_code=404, detail="Change not found")
        
        return diff_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get change diff: {str(e)}")


@router.post("/changes/revert/{change_id}")
async def revert_change(change_id: str, request: RevertChangeRequest):
    """
    Revert a specific change
    """
    try:
        success, revert_data = change_tracker.revert_change(
            user_id=request.user_id,
            change_id=change_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Change not found or cannot be reverted")
        
        return {
            "message": f"Change {change_id} reverted successfully",
            "revert_data": revert_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revert change: {str(e)}")



