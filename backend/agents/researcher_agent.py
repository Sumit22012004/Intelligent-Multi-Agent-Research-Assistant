"""
Research Agent - Gathers information from multiple sources.
"""

from typing import Dict, List
from loguru import logger

from backend.services.llm_service import gemini_service
from backend.services.arxiv_service import arxiv_service
from backend.services.perplexity_service import perplexity_service
from backend.services.vector_storage_service import vector_storage_service
from backend.core.prompts import get_agent_prompt, format_research_query
from backend.core.config import settings


class ResearcherAgent:
    """Agent responsible for gathering research information."""
    
    def __init__(self):
        self.agent_type = "researcher"
        self.system_prompt = get_agent_prompt(self.agent_type)
    
    async def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search arXiv for relevant papers."""
        try:
            papers = await arxiv_service.search_papers(query, max_results=max_results)
            logger.info(f"Found {len(papers)} papers on arXiv")
            return papers
        except Exception as error:
            logger.error(f"arXiv search failed: {error}")
            return []
    
    async def search_web(self, query: str) -> Dict[str, str]:
        """Search the web using Perplexity."""
        try:
            result = await perplexity_service.search_with_focus(query, focus="academic")
            logger.info("Web search completed")
            return result
        except Exception as error:
            logger.error(f"Web search failed: {error}")
            return {"content": "", "citations": ""}
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Search user's uploaded documents."""
        try:
            results = await vector_storage_service.search_similar_chunks(
                query=query,
                limit=limit,
                user_id=settings.user_id
            )
            logger.info(f"Found {len(results)} relevant document chunks")
            return results
        except Exception as error:
            logger.error(f"Document search failed: {error}")
            return []
    
    async def conduct_research(
        self, 
        query: str,
        use_arxiv: bool = True,
        use_web: bool = True,
        use_documents: bool = True
    ) -> Dict[str, any]:
        """
        Conduct comprehensive research from multiple sources.
        
        Args:
            query: Research query
            use_arxiv: Whether to search arXiv
            use_web: Whether to search the web
            use_documents: Whether to search uploaded documents
            
        Returns:
            Research findings from all sources
        """
        try:
            research_results = {
                "query": query,
                "arxiv_papers": [],
                "web_results": {},
                "document_chunks": [],
                "sources_count": 0
            }
            
            # Search arXiv
            if use_arxiv:
                arxiv_query = format_research_query("arxiv_search", query)
                research_results["arxiv_papers"] = await self.search_arxiv(query, max_results=5)
                research_results["sources_count"] += len(research_results["arxiv_papers"])
            
            # Search web
            if use_web:
                web_query = format_research_query("web_search", query)
                research_results["web_results"] = await self.search_web(query)
                if research_results["web_results"].get("content"):
                    research_results["sources_count"] += 1
            
            # Search documents
            if use_documents:
                doc_query = format_research_query("document_search", query)
                research_results["document_chunks"] = await self.search_documents(query, limit=5)
                research_results["sources_count"] += len(research_results["document_chunks"])
            
            logger.info(f"Research completed: {research_results['sources_count']} sources found")
            return research_results
            
        except Exception as error:
            logger.error(f"Research failed: {error}")
            raise
    
    async def synthesize_findings(self, research_results: Dict[str, any]) -> str:
        """
        Use LLM to synthesize research findings into a structured report.
        
        Args:
            research_results: Raw research results
            
        Returns:
            Synthesized research report
        """
        try:
            # Build comprehensive research context
            context_parts = []
            
            # Add arXiv papers
            if research_results.get("arxiv_papers"):
                context_parts.append("=== ARXIV PAPERS ===")
                for paper in research_results["arxiv_papers"][:3]:  # Top 3
                    context_parts.append(f"\nTitle: {paper['title']}")
                    context_parts.append(f"Authors: {paper['authors']}")
                    context_parts.append(f"Summary: {paper['summary'][:500]}...")
                    context_parts.append(f"URL: {paper['pdf_url']}\n")
            
            # Add web results
            if research_results.get("web_results", {}).get("content"):
                context_parts.append("\n=== WEB SEARCH RESULTS ===")
                context_parts.append(research_results["web_results"]["content"])
                if research_results["web_results"].get("citations"):
                    context_parts.append(f"\nCitations: {research_results['web_results']['citations']}")
            
            # Add document chunks
            if research_results.get("document_chunks"):
                context_parts.append("\n=== USER DOCUMENTS ===")
                for chunk in research_results["document_chunks"][:3]:  # Top 3
                    context_parts.append(f"\nFrom: {chunk['file_name']}")
                    context_parts.append(f"Content: {chunk['text'][:300]}...")
                    context_parts.append(f"Relevance: {chunk['score']}\n")
            
            research_context = "\n".join(context_parts)
            
            # Create synthesis prompt
            prompt = f"""{self.system_prompt}

Research Query: {research_results['query']}

Research Findings:
{research_context}

Task: Synthesize these research findings into a clear, organized report with proper citations.
Focus on the most relevant and reliable information."""
            
            # Generate synthesis
            synthesis = await gemini_service.generate_text(prompt)
            
            logger.info("Research findings synthesized")
            return synthesis
            
        except Exception as error:
            logger.error(f"Failed to synthesize findings: {error}")
            raise


# Global researcher agent instance
researcher_agent = ResearcherAgent()

