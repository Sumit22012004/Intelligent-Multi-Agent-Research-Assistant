"""Perplexity web search service."""

import httpx
from typing import Dict
from loguru import logger
from backend.core.config import settings


class PerplexitySearchService:
    """Handles web search using Perplexity API."""
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"
        self.model = "llama-3.1-sonar-small-128k-online"
    
    async def search_web(self, query: str, max_results: int = 5) -> Dict[str, str]:
        """
        Search the web using Perplexity API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results (not directly supported, included for API consistency)
            
        Returns:
            Dictionary with search results and sources
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful research assistant that provides accurate information with citations."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract response content and citations
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                
                result = {
                    "query": query,
                    "content": content,
                    "citations": ", ".join(citations) if citations else "No citations available",
                    "model": self.model
                }
                
                logger.info(f"Web search completed for query: {query}")
                return result
                
        except httpx.HTTPStatusError as error:
            logger.error(f"Perplexity API HTTP error: {error.response.status_code} - {error.response.text}")
            raise
        except Exception as error:
            logger.error(f"Failed to search web with Perplexity: {error}")
            raise
    
    async def search_with_focus(self, query: str, focus: str = "internet") -> Dict[str, str]:
        """
        Search with specific focus (internet, academic, writing, wolfram, youtube, reddit).
        
        Args:
            query: Search query string
            focus: Search focus type
            
        Returns:
            Dictionary with search results and sources
        """
        try:
            # Map focus to appropriate model
            focus_models = {
                "internet": "llama-3.1-sonar-small-128k-online",
                "academic": "llama-3.1-sonar-small-128k-online",
                "general": "llama-3.1-sonar-small-128k-online"
            }
            
            model = focus_models.get(focus, self.model)
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                system_prompts = {
                    "academic": "You are an academic research assistant. Provide scholarly information with proper citations.",
                    "internet": "You are a helpful research assistant that provides accurate information with citations.",
                    "general": "You are a helpful assistant that provides accurate information."
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompts.get(focus, system_prompts["general"])
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                
                result = {
                    "query": query,
                    "focus": focus,
                    "content": content,
                    "citations": ", ".join(citations) if citations else "No citations available",
                    "model": model
                }
                
                logger.info(f"Focused web search completed: {query} (focus: {focus})")
                return result
                
        except httpx.HTTPStatusError as error:
            logger.error(f"Perplexity API HTTP error: {error.response.status_code} - {error.response.text}")
            raise
        except Exception as error:
            logger.error(f"Failed to search web with focus: {error}")
            raise


# Global Perplexity service instance
perplexity_service = PerplexitySearchService()

