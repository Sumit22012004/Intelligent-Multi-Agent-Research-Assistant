"""Memory management service for persistent conversation history."""

from typing import List, Dict
from datetime import datetime, timezone
from loguru import logger

from backend.database.mongodb import mongodb_connection
from backend.database.models.models import Session, Conversation
from backend.core.config import settings


class MemoryService:
    """Handles conversation memory and session management."""
    
    def __init__(self):
        self.user_id = settings.user_id
    
    async def create_session(self, title: str = "New Research Session") -> str:
        """
        Create a new research session.
        
        Args:
            title: Session title
            
        Returns:
            Session ID
        """
        try:
            db = mongodb_connection.get_database()
            sessions_collection = db["sessions"]
            
            # Generate session ID
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            session_id = f"session_{self.user_id}_{timestamp}"
            
            # Create session document
            session = Session(
                session_id=session_id,
                user_id=self.user_id,
                title=title,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                is_active=True,
                message_count=0
            )
            
            await sessions_collection.insert_one(session.model_dump())
            
            logger.info(f"Created new session: {session_id}")
            return session_id
            
        except Exception as error:
            logger.error(f"Failed to create session: {error}")
            raise
    
    async def get_active_session(self) -> str:
        """
        Get the current active session or create a new one.
        
        Returns:
            Session ID
        """
        try:
            db = mongodb_connection.get_database()
            sessions_collection = db["sessions"]
            
            # Find active session
            active_session = await sessions_collection.find_one({
                "user_id": self.user_id,
                "is_active": True
            })
            
            if active_session:
                return active_session["session_id"]
            
            # Create new session if none exists
            return await self.create_session()
            
        except Exception as error:
            logger.error(f"Failed to get active session: {error}")
            raise
    
    async def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        try:
            db = mongodb_connection.get_database()
            conversations_collection = db["conversations"]
            
            # Get recent messages
            cursor = conversations_collection.find(
                {"session_id": session_id}
            ).sort("timestamp", -1).limit(limit)
            
            messages = await cursor.to_list(length=limit)
            
            # Reverse to get chronological order
            messages.reverse()
            
            # Format messages
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat() if isinstance(msg["timestamp"], datetime) else msg["timestamp"],
                    "agent_type": msg.get("agent_type", ""),
                    "sources": msg.get("sources", [])
                })
            
            logger.info(f"Retrieved {len(formatted_messages)} messages from session: {session_id}")
            return formatted_messages
            
        except Exception as error:
            logger.error(f"Failed to get session history: {error}")
            raise
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        agent_type: str = "",
        sources: List[str] = None,
        processing_time: float = 0.0
    ) -> bool:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role (user or assistant)
            content: Message content
            agent_type: Type of agent that generated the message
            sources: List of sources used
            processing_time: Time taken to process
            
        Returns:
            True if successful
        """
        try:
            db = mongodb_connection.get_database()
            conversations_collection = db["conversations"]
            sessions_collection = db["sessions"]
            
            # Create conversation message
            conversation = Conversation(
                session_id=session_id,
                user_id=self.user_id,
                role=role,
                content=content,
                timestamp=datetime.now(timezone.utc),
                agent_type=agent_type,
                sources=sources or [],
                processing_time=processing_time
            )
            
            await conversations_collection.insert_one(conversation.model_dump())
            
            # Update session
            await sessions_collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                    "$inc": {"message_count": 1}
                }
            )
            
            logger.info(f"Added {role} message to session: {session_id}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to add message: {error}")
            raise
    
    async def get_all_sessions(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        Get all sessions for the user.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session information
        """
        try:
            db = mongodb_connection.get_database()
            sessions_collection = db["sessions"]
            
            # Get sessions sorted by updated_at
            cursor = sessions_collection.find(
                {"user_id": self.user_id}
            ).sort("updated_at", -1).limit(limit)
            
            sessions = await cursor.to_list(length=limit)
            
            # Format sessions
            formatted_sessions = []
            for session in sessions:
                formatted_sessions.append({
                    "session_id": session["session_id"],
                    "title": session["title"],
                    "created_at": session["created_at"].isoformat() if isinstance(session["created_at"], datetime) else session["created_at"],
                    "updated_at": session["updated_at"].isoformat() if isinstance(session["updated_at"], datetime) else session["updated_at"],
                    "is_active": str(session["is_active"]),
                    "message_count": str(session["message_count"])
                })
            
            logger.info(f"Retrieved {len(formatted_sessions)} sessions")
            return formatted_sessions
            
        except Exception as error:
            logger.error(f"Failed to get sessions: {error}")
            raise
    
    async def deactivate_all_sessions(self) -> bool:
        """
        Deactivate all user sessions.
        
        Returns:
            True if successful
        """
        try:
            db = mongodb_connection.get_database()
            sessions_collection = db["sessions"]
            
            await sessions_collection.update_many(
                {"user_id": self.user_id},
                {"$set": {"is_active": False}}
            )
            
            logger.info("Deactivated all user sessions")
            return True
            
        except Exception as error:
            logger.error(f"Failed to deactivate sessions: {error}")
            raise
    
    async def activate_session(self, session_id: str) -> bool:
        """
        Activate a specific session (and deactivate others).
        
        Args:
            session_id: Session to activate
            
        Returns:
            True if successful
        """
        try:
            # Deactivate all sessions first
            await self.deactivate_all_sessions()
            
            # Activate the specified session
            db = mongodb_connection.get_database()
            sessions_collection = db["sessions"]
            
            await sessions_collection.update_one(
                {"session_id": session_id},
                {"$set": {"is_active": True}}
            )
            
            logger.info(f"Activated session: {session_id}")
            return True
            
        except Exception as error:
            logger.error(f"Failed to activate session: {error}")
            raise


# Global memory service instance
memory_service = MemoryService()

