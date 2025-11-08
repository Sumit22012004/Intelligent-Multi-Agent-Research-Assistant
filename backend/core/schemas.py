"""
Pydantic schemas for data validation.
All data structures used across the application.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel


class MessageSchema(BaseModel):
    """A single message in a conversation."""
    role: str
    content: str
    timestamp: datetime


class DocumentMetadata(BaseModel):
    """Metadata for an uploaded document."""
    document_id: str
    file_name: str
    file_type: str
    file_size: str
    chunk_count: str
    created_at: str


class DocumentProcessingStatus(BaseModel):
    """Status of document processing."""
    document_id: str
    file_name: str
    status: str
    message: str
    chunk_count: int


class ResearchQueryRequest(BaseModel):
    """Request schema for research queries."""
    session_id: str
    query: str


class ResearchQueryResponse(BaseModel):
    """Response schema for research queries."""
    answer: str
    sources: List[str]
    processing_time: float
    confidence: float


class SessionInfo(BaseModel):
    """Information about a research session."""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
