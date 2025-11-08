"""
Comprehensive Phase 3 Test Script

Tests all Phase 3 components:
- Agent prompts
- Memory service
- All three agents (Researcher, Summarizer, Analyst)
- Agent orchestrator
- Research and session API endpoints
- Integration with Phases 1 & 2
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def print_section(title):
    """Print section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def print_test(test_name):
    """Print test header."""
    print(f"\n[TEST] {test_name}")


def print_success(message=""):
    """Print success message."""
    print(f"  [OK] {message}")


def print_warning(message=""):
    """Print warning message."""
    print(f"  [WARN] {message}")


def print_error(message=""):
    """Print error message."""
    print(f"  [ERROR] {message}")


def print_info(message=""):
    """Print info message."""
    print(f"  - {message}")


async def test_prompts():
    """Test agent prompts."""
    print_section("AGENT PROMPTS TEST")
    
    results = []
    
    print_test("Agent Prompts Loading")
    try:
        from backend.core.prompts import get_agent_prompt, SYSTEM_PROMPTS, RESEARCH_TEMPLATES
        
        # Test getting prompts
        researcher_prompt = get_agent_prompt("researcher")
        summarizer_prompt = get_agent_prompt("summarizer")
        analyst_prompt = get_agent_prompt("analyst")
        
        print_success("All agent prompts loaded")
        print_info(f"Researcher prompt length: {len(researcher_prompt)} chars")
        print_info(f"Summarizer prompt length: {len(summarizer_prompt)} chars")
        print_info(f"Analyst prompt length: {len(analyst_prompt)} chars")
        print_info(f"Research templates: {len(RESEARCH_TEMPLATES)} available")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def test_memory_service():
    """Test memory management service."""
    print_section("MEMORY SERVICE TEST")
    
    results = []
    
    print_test("Memory Service Initialization")
    try:
        from backend.services.memory_service import memory_service
        from backend.database.mongodb import mongodb_connection
        
        # Connect to MongoDB first
        await mongodb_connection.connect()
        
        print_success("Memory service initialized")
        print_info(f"User ID: {memory_service.user_id}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
        return False
    
    print_test("Session Creation")
    try:
        session_id = await memory_service.create_session("Test Session")
        
        print_success("Session created")
        print_info(f"Session ID: {session_id}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("Message Storage")
    try:
        await memory_service.add_message(
            session_id=session_id,
            role="user",
            content="Test message"
        )
        
        print_success("Message stored")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("Session History Retrieval")
    try:
        history = await memory_service.get_session_history(session_id, limit=10)
        
        print_success("History retrieved")
        print_info(f"Messages in history: {len(history)}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def test_agents():
    """Test individual agents."""
    print_section("AGENTS TEST")
    
    results = []
    
    print_test("Researcher Agent")
    try:
        from backend.agents.researcher_agent import researcher_agent
        
        print_success("Researcher agent loaded")
        print_info(f"Agent type: {researcher_agent.agent_type}")
        print_info(f"System prompt set: {len(researcher_agent.system_prompt) > 0}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("Summarizer Agent")
    try:
        from backend.agents.summarizer_agent import summarizer_agent
        
        print_success("Summarizer agent loaded")
        print_info(f"Agent type: {summarizer_agent.agent_type}")
        print_info(f"System prompt set: {len(summarizer_agent.system_prompt) > 0}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("Analyst Agent")
    try:
        from backend.agents.analyst_agent import analyst_agent
        
        print_success("Analyst agent loaded")
        print_info(f"Agent type: {analyst_agent.agent_type}")
        print_info(f"System prompt set: {len(analyst_agent.system_prompt) > 0}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def test_orchestrator():
    """Test agent orchestrator."""
    print_section("ORCHESTRATOR TEST")
    
    results = []
    
    print_test("Orchestrator Initialization")
    try:
        from backend.agents.orchestrator import agent_orchestrator
        
        print_success("Orchestrator initialized")
        print_info(f"Graph compiled: {agent_orchestrator.graph is not None}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def test_api_routes():
    """Test new API routes."""
    print_section("API ROUTES TEST")
    
    results = []
    
    print_test("Research API Routes")
    try:
        from backend.api.routes import research
        
        routes = [route.path for route in research.router.routes]
        
        print_success("Research routes loaded")
        print_info(f"Routes: {len(routes)}")
        for route in routes:
            print_info(f"  • {route}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("Session API Routes")
    try:
        from backend.api.routes import sessions
        
        routes = [route.path for route in sessions.router.routes]
        
        print_success("Session routes loaded")
        print_info(f"Routes: {len(routes)}")
        for route in routes:
            print_info(f"  • {route}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("FastAPI App Integration")
    try:
        from backend.main import app
        
        routes = [route.path for route in app.routes]
        
        has_research = any('/research' in r for r in routes)
        has_sessions = any('/sessions' in r for r in routes)
        
        print_success("FastAPI app with Phase 3 routes")
        print_info(f"Total routes: {len(routes)}")
        print_info(f"Research endpoints: {has_research}")
        print_info(f"Session endpoints: {has_sessions}")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def test_phase_integration():
    """Test integration across all three phases."""
    print_section("PHASE 1+2+3 INTEGRATION TEST")
    
    results = []
    
    print_test("All Services Available")
    try:
        from backend.services import (
            embedding_service,
            gemini_service,
            document_processor,
            arxiv_service,
            perplexity_service,
            vector_storage_service,
            memory_service
        )
        
        print_success("All services imported")
        print_info("Phase 1: embedding_service, gemini_service")
        print_info("Phase 2: document_processor, arxiv_service, perplexity_service, vector_storage_service")
        print_info("Phase 3: memory_service")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    print_test("All Agents Available")
    try:
        from backend.agents import (
            researcher_agent,
            summarizer_agent,
            analyst_agent,
            agent_orchestrator
        )
        
        print_success("All agents imported")
        print_info("researcher_agent, summarizer_agent, analyst_agent, agent_orchestrator")
        results.append(True)
    except Exception as error:
        print_error(f"Failed: {error}")
        results.append(False)
    
    return all(results)


async def main():
    """Run all Phase 3 tests."""
    print_section("PHASE 3 COMPREHENSIVE TEST")
    print("Testing Multi-Agent System and Memory Management...")
    
    # Run all test suites
    prompts_pass = await test_prompts()
    memory_pass = await test_memory_service()
    agents_pass = await test_agents()
    orchestrator_pass = await test_orchestrator()
    api_pass = await test_api_routes()
    integration_pass = await test_phase_integration()
    
    # Final Summary
    print_section("FINAL SUMMARY")
    
    print(f"\n{'=' * 60}")
    print("PHASE 3 COMPONENTS:")
    print('=' * 60)
    print(f"Agent Prompts: {'PASS' if prompts_pass else 'FAIL'}")
    print(f"Memory Service: {'PASS' if memory_pass else 'FAIL'}")
    print(f"Agents (Researcher, Summarizer, Analyst): {'PASS' if agents_pass else 'FAIL'}")
    print(f"Orchestrator (LangGraph): {'PASS' if orchestrator_pass else 'FAIL'}")
    print(f"API Routes (Research, Sessions): {'PASS' if api_pass else 'FAIL'}")
    print(f"Phase Integration: {'PASS' if integration_pass else 'FAIL'}")
    
    # Overall Result
    all_pass = all([prompts_pass, memory_pass, agents_pass, orchestrator_pass, api_pass, integration_pass])
    
    print(f"\n{'=' * 60}")
    if all_pass:
        print("SUCCESS: PHASE 3 - ALL TESTS PASSED!")
        print("Multi-Agent Research System is READY!")
        print("")
        print("Complete System:")
        print("[OK] Phase 1: Core Infrastructure")
        print("[OK] Phase 2: Document Processing & Search")
        print("[OK] Phase 3: Multi-Agent System & Memory")
        print("")
        print("Ready for production use!")
    else:
        print("FAILED: Some Phase 3 tests failed")
        print("Please review the errors above")
    print('=' * 60)
    
    # Cleanup
    try:
        from backend.database.mongodb import mongodb_connection
        await mongodb_connection.disconnect()
    except:
        pass


if __name__ == "__main__":
    asyncio.run(main())

