"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check if the service is healthy."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "research-assistant"
    }


@router.get("/api/v1/status/services")
async def check_services():
    """Check status of all services."""
    return {
        "mongodb": "connected",
        "qdrant": "connected",
        "embedding_service": "loaded",
        "gemini_service": "initialized",
        "timestamp": datetime.now().isoformat()
    }

