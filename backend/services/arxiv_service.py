"""arXiv paper search service."""

import arxiv
from typing import List, Dict
from loguru import logger


class ArxivSearchService:
    """Handles searching and retrieving papers from arXiv."""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    async def search_papers(
        self, 
        query: str, 
        max_results: int = 10,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance
    ) -> List[Dict[str, str]]:
        """
        Search for papers on arXiv.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criterion for results
            
        Returns:
            List of paper information dictionaries
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_by
            )
            
            papers = []
            
            for result in self.client.results(search):
                paper_info = {
                    "title": result.title,
                    "authors": ", ".join([author.name for author in result.authors]),
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "updated": result.updated.strftime("%Y-%m-%d"),
                    "arxiv_id": result.entry_id.split("/")[-1],
                    "pdf_url": result.pdf_url,
                    "primary_category": result.primary_category,
                    "categories": ", ".join(result.categories),
                    "doi": result.doi if result.doi else "",
                    "journal_ref": result.journal_ref if result.journal_ref else ""
                }
                
                papers.append(paper_info)
            
            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers
            
        except Exception as error:
            logger.error(f"Failed to search arXiv: {error}")
            raise
    
    async def get_paper_by_id(self, arxiv_id: str) -> Dict[str, str]:
        """
        Get a specific paper by its arXiv ID.
        
        Args:
            arxiv_id: The arXiv ID (e.g., "2301.12345")
            
        Returns:
            Paper information dictionary
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            
            result = next(self.client.results(search))
            
            paper_info = {
                "title": result.title,
                "authors": ", ".join([author.name for author in result.authors]),
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": result.updated.strftime("%Y-%m-%d"),
                "arxiv_id": result.entry_id.split("/")[-1],
                "pdf_url": result.pdf_url,
                "primary_category": result.primary_category,
                "categories": ", ".join(result.categories),
                "doi": result.doi if result.doi else "",
                "journal_ref": result.journal_ref if result.journal_ref else ""
            }
            
            logger.info(f"Retrieved paper: {arxiv_id}")
            return paper_info
            
        except Exception as error:
            logger.error(f"Failed to get arXiv paper: {error}")
            raise
    
    async def download_paper_pdf(self, arxiv_id: str, download_path: str) -> str:
        """
        Download paper PDF from arXiv.
        
        Args:
            arxiv_id: The arXiv ID
            download_path: Directory to save the PDF
            
        Returns:
            Path to downloaded PDF file
        """
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(self.client.results(search))
            
            pdf_path = paper.download_pdf(dirpath=download_path)
            
            logger.info(f"Downloaded paper {arxiv_id} to {pdf_path}")
            return pdf_path
            
        except Exception as error:
            logger.error(f"Failed to download arXiv paper: {error}")
            raise


# Global arXiv service instance
arxiv_service = ArxivSearchService()

