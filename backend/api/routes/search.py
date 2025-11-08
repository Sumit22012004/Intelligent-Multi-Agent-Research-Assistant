"""Search API routes (arXiv and Perplexity)."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from loguru import logger

from backend.services.arxiv_service import arxiv_service
from backend.services.perplexity_service import perplexity_service


router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("/arxiv", response_model=List[Dict[str, str]])
async def search_arxiv(
    query: str = Query(..., description="Search query for arXiv papers"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    """
    Search for papers on arXiv.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (1-50)
        
    Returns:
        List of paper information
    """
    try:
        papers = await arxiv_service.search_papers(query, max_results=max_results)
        
        logger.info(f"arXiv search completed: {query}")
        return papers
        
    except Exception as error:
        logger.error(f"arXiv search failed: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to search arXiv: {str(error)}")


@router.get("/arxiv/{arxiv_id}", response_model=Dict[str, str])
async def get_arxiv_paper(arxiv_id: str):
    """
    Get a specific paper by arXiv ID.
    
    Args:
        arxiv_id: The arXiv ID (e.g., "2301.12345")
        
    Returns:
        Paper information
    """
    try:
        paper = await arxiv_service.get_paper_by_id(arxiv_id)
        
        logger.info(f"Retrieved arXiv paper: {arxiv_id}")
        return paper
        
    except Exception as error:
        logger.error(f"Failed to get arXiv paper: {error}")
        raise HTTPException(status_code=404, detail=f"Paper not found: {str(error)}")


@router.get("/web", response_model=Dict[str, str])
async def search_web(
    query: str = Query(..., description="Search query for web search"),
    focus: str = Query("internet", description="Search focus (internet, academic, general)")
):
    """
    Search the web using Perplexity API.
    
    Args:
        query: Search query string
        focus: Search focus type
        
    Returns:
        Search results with citations
    """
    try:
        if focus == "internet" or focus == "academic":
            result = await perplexity_service.search_with_focus(query, focus=focus)
        else:
            result = await perplexity_service.search_web(query)
        
        logger.info(f"Web search completed: {query}")
        return result
        
    except Exception as error:
        logger.error(f"Web search failed: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to search web: {str(error)}")


@router.get("/semantic", response_model=List[Dict[str, str]])
async def semantic_search(
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
    document_id: str = Query(None, description="Filter by document ID")
):
    """
    Perform semantic search on uploaded documents.
    
    Args:
        query: Search query string
        limit: Maximum number of results (1-20)
        document_id: Optional document ID to filter results
        
    Returns:
        List of similar chunks with scores
    """
    try:
        from backend.services.vector_storage_service import vector_storage_service
        from backend.core.config import settings
        
        results = await vector_storage_service.search_similar_chunks(
            query=query,
            limit=limit,
            user_id=settings.user_id,
            document_id=document_id
        )
        
        logger.info(f"Semantic search completed: {query}")
        return results
        
    except Exception as error:
        logger.error(f"Semantic search failed: {error}")
        raise HTTPException(status_code=500, detail=f"Failed to perform semantic search: {str(error)}")

