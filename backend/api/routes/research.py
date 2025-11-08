"""Research query API routes."""

from fastapi import APIRouter, HTTPException
from typing import Dict
from loguru import logger

from backend.agents.orchestrator import agent_orchestrator
from backend.core.schemas import ResearchQueryRequest, ResearchQueryResponse


router = APIRouter(prefix="/api/v1/research", tags=["research"])


@router.post("/query", response_model=ResearchQueryResponse)
async def process_research_query(request: ResearchQueryRequest):
    """
    Process a research query through the multi-agent system.
    
    Args:
        request: Research query request with session_id and query
        
    Returns:
        Research response with answer, sources, and metadata
    """
    try:
        logger.info(f"Received research query: {request.query}")
        
        # Process through agent orchestrator
        result = await agent_orchestrator.process_query(
            query=request.query,
            session_id=request.session_id if request.session_id else None
        )
        
        return ResearchQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            processing_time=result["processing_time"],
            confidence=0.85  # Placeholder - can be calculated based on sources
        )
        
    except Exception as error:
        logger.error(f"Failed to process research query: {error}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process query: {str(error)}"
        )


@router.post("/quick-answer")
async def get_quick_answer(query: str):
    """
    Get a quick answer without full research workflow.
    Uses only the LLM without multi-agent processing.
    
    Args:
        query: Simple question
        
    Returns:
        Quick answer
    """
    try:
        from backend.services.llm_service import gemini_service
        
        answer = await gemini_service.generate_text(query)
        
        return {
            "answer": answer,
            "type": "quick",
            "sources": []
        }
        
    except Exception as error:
        logger.error(f"Failed to get quick answer: {error}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get answer: {str(error)}"
        )

