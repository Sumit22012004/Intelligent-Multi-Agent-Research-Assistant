"""
Agent Orchestrator using LangGraph for workflow management.
Coordinates between Researcher, Summarizer, and Analyst agents.
"""

from typing import Dict, List, TypedDict
from datetime import datetime
import time
from loguru import logger

from langgraph.graph import StateGraph, END
from backend.agents.researcher_agent import researcher_agent
from backend.agents.summarizer_agent import summarizer_agent
from backend.agents.analyst_agent import analyst_agent
from backend.services.memory_service import memory_service


class AgentState(TypedDict):
    """State shared between agents in the workflow."""
    query: str
    session_id: str
    conversation_history: List[Dict[str, str]]
    research_results: Dict[str, any]
    research_synthesis: str
    summary: str
    final_answer: str
    sources: List[str]
    current_step: str
    processing_time: float
    error: str


class AgentOrchestrator:
    """Orchestrates the multi-agent research workflow."""
    
    def __init__(self):
        self.graph = self.build_graph()
    
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Define the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("researcher", self.research_node)
        workflow.add_node("summarizer", self.summarizer_node)
        workflow.add_node("analyst", self.analyst_node)
        
        # Define the workflow edges
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "summarizer")
        workflow.add_edge("summarizer", "analyst")
        workflow.add_edge("analyst", END)
        
        return workflow.compile()
    
    async def research_node(self, state: AgentState) -> AgentState:
        """Research phase - gather information."""
        try:
            logger.info(f"Starting research phase for query: {state['query']}")
            state["current_step"] = "research"
            
            # Conduct research
            research_results = await researcher_agent.conduct_research(
                query=state["query"],
                use_arxiv=True,
                use_web=True,
                use_documents=True
            )
            
            state["research_results"] = research_results
            
            # Synthesize findings
            research_synthesis = await researcher_agent.synthesize_findings(research_results)
            state["research_synthesis"] = research_synthesis
            
            # Extract sources
            sources = []
            for paper in research_results.get("arxiv_papers", []):
                sources.append(paper.get("pdf_url", ""))
            if research_results.get("web_results", {}).get("citations"):
                sources.append(research_results["web_results"]["citations"])
            
            state["sources"] = sources
            
            logger.info("Research phase completed")
            return state
            
        except Exception as error:
            logger.error(f"Research phase failed: {error}")
            state["error"] = str(error)
            return state
    
    async def summarizer_node(self, state: AgentState) -> AgentState:
        """Summarizer phase - organize and condense findings."""
        try:
            logger.info("Starting summarizer phase")
            state["current_step"] = "summarizer"
            
            # Create summary
            summary = await summarizer_agent.summarize(
                research_synthesis=state["research_synthesis"],
                original_query=state["query"]
            )
            
            state["summary"] = summary
            
            logger.info("Summarizer phase completed")
            return state
            
        except Exception as error:
            logger.error(f"Summarizer phase failed: {error}")
            state["error"] = str(error)
            return state
    
    async def analyst_node(self, state: AgentState) -> AgentState:
        """Analyst phase - provide insights and final answer."""
        try:
            logger.info("Starting analyst phase")
            state["current_step"] = "analyst"
            
            # Create analysis
            analysis = await analyst_agent.analyze(
                summary=state["summary"],
                original_query=state["query"],
                conversation_history=state.get("conversation_history", [])
            )
            
            state["final_answer"] = analysis
            
            logger.info("Analyst phase completed")
            return state
            
        except Exception as error:
            logger.error(f"Analyst phase failed: {error}")
            state["error"] = str(error)
            return state
    
    async def process_query(
        self, 
        query: str, 
        session_id: str = None
    ) -> Dict[str, any]:
        """
        Process a research query through the agent workflow.
        
        Args:
            query: User's research question
            session_id: Session ID for context
            
        Returns:
            Final response with answer and metadata
        """
        try:
            start_time = time.time()
            
            # Get or create session
            if not session_id:
                session_id = await memory_service.get_active_session()
            
            # Get conversation history
            conversation_history = await memory_service.get_session_history(session_id, limit=10)
            
            # Initialize state
            initial_state: AgentState = {
                "query": query,
                "session_id": session_id,
                "conversation_history": conversation_history,
                "research_results": {},
                "research_synthesis": "",
                "summary": "",
                "final_answer": "",
                "sources": [],
                "current_step": "init",
                "processing_time": 0.0,
                "error": ""
            }
            
            logger.info(f"Processing query: {query}")
            
            # Run the workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time
            
            # Save user message
            await memory_service.add_message(
                session_id=session_id,
                role="user",
                content=query
            )
            
            # Save assistant response
            await memory_service.add_message(
                session_id=session_id,
                role="assistant",
                content=final_state["final_answer"],
                agent_type="analyst",
                sources=final_state["sources"],
                processing_time=processing_time
            )
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            
            return {
                "answer": final_state["final_answer"],
                "sources": final_state["sources"],
                "processing_time": processing_time,
                "session_id": session_id,
                "sources_count": final_state["research_results"].get("sources_count", 0)
            }
            
        except Exception as error:
            logger.error(f"Failed to process query: {error}")
            raise


# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()

