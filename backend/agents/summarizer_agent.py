"""
Summarizer Agent - Synthesizes and organizes research findings.
"""

from typing import Dict
from loguru import logger

from backend.services.llm_service import gemini_service
from backend.core.prompts import get_agent_prompt


class SummarizerAgent:
    """Agent responsible for summarizing research findings."""
    
    def __init__(self):
        self.agent_type = "summarizer"
        self.system_prompt = get_agent_prompt(self.agent_type)
    
    async def summarize(self, research_synthesis: str, original_query: str) -> str:
        """
        Summarize research findings into a concise, organized format.
        
        Args:
            research_synthesis: Synthesized research from Researcher
            original_query: Original user query
            
        Returns:
            Summarized findings
        """
        try:
            prompt = f"""{self.system_prompt}

Original Question: {original_query}

Research Findings:
{research_synthesis}

Task: Create a clear, concise summary of these research findings.
Organize by key themes, highlight main points, and preserve important citations."""
            
            summary = await gemini_service.generate_text(prompt)
            
            logger.info("Research summary created")
            return summary
            
        except Exception as error:
            logger.error(f"Failed to create summary: {error}")
            raise


# Global summarizer agent instance
summarizer_agent = SummarizerAgent()

