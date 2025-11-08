"""
Analyst Agent - Provides critical analysis and insights.
"""

from typing import Dict, List
from loguru import logger

from backend.services.llm_service import gemini_service
from backend.core.prompts import get_agent_prompt


class AnalystAgent:
    """Agent responsible for analyzing and interpreting research."""
    
    def __init__(self):
        self.agent_type = "analyst"
        self.system_prompt = get_agent_prompt(self.agent_type)
    
    async def analyze(
        self, 
        summary: str, 
        original_query: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Analyze summarized research and provide insights.
        
        Args:
            summary: Summarized research findings
            original_query: Original user query
            conversation_history: Previous conversation for context
            
        Returns:
            Analysis and final answer
        """
        try:
            # Build context from conversation history
            history_context = ""
            if conversation_history:
                history_context = "\n\nPrevious Conversation Context:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages
                    history_context += f"{msg['role']}: {msg['content'][:200]}...\n"
            
            prompt = f"""{self.system_prompt}

Original Question: {original_query}
{history_context}

Research Summary:
{summary}

Task: Provide a comprehensive analysis that:
1. Directly answers the user's question
2. Identifies key insights and patterns
3. Discusses implications and significance
4. Notes any limitations or gaps
5. Offers actionable takeaways or recommendations

Be thorough yet clear. Support your analysis with evidence from the research."""
            
            analysis = await gemini_service.generate_text(prompt)
            
            logger.info("Analysis completed")
            return analysis
            
        except Exception as error:
            logger.error(f"Failed to create analysis: {error}")
            raise


# Global analyst agent instance
analyst_agent = AnalystAgent()

