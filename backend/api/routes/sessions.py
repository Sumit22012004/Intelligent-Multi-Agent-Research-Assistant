"""Session management API routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from loguru import logger

from backend.services.memory_service import memory_service
from backend.core.schemas import SessionInfo


router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/create")
async def create_session(title: str = Query("New Research Session")):
    """
    Create a new research session.
    
    Args:
        title: Session title
        
    Returns:
        New session ID
    """
    try:
        session_id = await memory_service.create_session(title=title)
        
        return {
            "session_id": session_id,
            "message": "Session created successfully"
        }
        
    except Exception as error:
        logger.error(f"Failed to create session: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(error)}"
        )


@router.get("/list", response_model=List[SessionInfo])
async def list_sessions(limit: int = Query(20, ge=1, le=100)):
    """
    List all user sessions.
    
    Args:
        limit: Maximum number of sessions to return
        
    Returns:
        List of session information
    """
    try:
        sessions = await memory_service.get_all_sessions(limit=limit)
        
        # Convert to SessionInfo schema
        session_infos = []
        for session in sessions:
            session_infos.append(SessionInfo(
                session_id=session["session_id"],
                title=session.get("title", "Research Session"),
                created_at=session["created_at"],
                updated_at=session["updated_at"],
                message_count=int(session["message_count"])
            ))
        
        return session_infos
        
    except Exception as error:
        logger.error(f"Failed to list sessions: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sessions: {str(error)}"
        )


@router.get("/{session_id}/history")
async def get_session_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Session identifier
        limit: Maximum number of messages
        
    Returns:
        Conversation history
    """
    try:
        history = await memory_service.get_session_history(session_id, limit=limit)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history
        }
        
    except Exception as error:
        logger.error(f"Failed to get session history: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve history: {str(error)}"
        )


@router.post("/{session_id}/activate")
async def activate_session(session_id: str):
    """
    Activate a specific session.
    
    Args:
        session_id: Session to activate
        
    Returns:
        Success message
    """
    try:
        await memory_service.activate_session(session_id)
        
        return {
            "message": f"Session {session_id} activated successfully"
        }
        
    except Exception as error:
        logger.error(f"Failed to activate session: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate session: {str(error)}"
        )


@router.get("/active")
async def get_active_session():
    """
    Get the current active session.
    
    Returns:
        Active session ID
    """
    try:
        session_id = await memory_service.get_active_session()
        
        return {
            "session_id": session_id,
            "is_active": True
        }
        
    except Exception as error:
        logger.error(f"Failed to get active session: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active session: {str(error)}"
        )

