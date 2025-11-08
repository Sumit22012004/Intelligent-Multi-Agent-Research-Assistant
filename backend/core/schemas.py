"""
Pydantic schemas for data validation.
All data structures used across the application.
"""

from datetime import datetime
from pydantic import BaseModel


class MessageSchema(BaseModel):
    """A single message in a conversation."""
    role: str
    content: str
    timestamp: datetime


class DocumentMetadata(BaseModel):
    """Metadata for an uploaded document."""
    document_id: str
    filename: str
    file_type: str
    file_size: int
    page_count: int
    upload_timestamp: datetime


class ResearchQueryRequest(BaseModel):
    """Request schema for research queries."""
    session_id: str
    query: str


class ResearchQueryResponse(BaseModel):
    """Response schema for research queries."""
    answer: str
    sources: list[str]
    processing_time: float
    confidence: float


class SessionInfo(BaseModel):
    """Information about a research session."""
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class DocumentProcessingStatus(BaseModel):
    """Status of document processing."""
    document_id: str
    status: str
    chunks_created: int
    processing_time: float

