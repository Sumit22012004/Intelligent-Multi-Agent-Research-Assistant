"""Database models for MongoDB collections."""

from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    """User profile model."""
    user_id: str
    username: str
    created_at: datetime
    total_sessions: int = 0
    total_documents: int = 0


class Session(BaseModel):
    """Research session model."""
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    message_count: int = 0


class Conversation(BaseModel):
    """Conversation message model."""
    session_id: str
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    agent_type: str = ""
    sources: list[str] = []
    processing_time: float = 0.0


class Document(BaseModel):
    """Uploaded document model."""
    document_id: str
    user_id: str
    session_id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    processing_status: str
    chunk_count: int = 0
    qdrant_ids: list[str] = []

