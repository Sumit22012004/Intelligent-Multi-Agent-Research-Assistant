"""Streamlit frontend for Intelligent Research Assistant."""

import streamlit as st
import requests
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "sessions_list" not in st.session_state:
        st.session_state.sessions_list = []


def check_backend_health():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_active_session():
    """Get or create active session."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/sessions/active")
        if response.status_code == 200:
            return response.json()["session_id"]
    except:
        pass
    return None


def load_session_history(session_id: str):
    """Load conversation history for a session."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/sessions/{session_id}/history",
            params={"limit": 50}
        )
        if response.status_code == 200:
            history = response.json()["messages"]
            st.session_state.messages = history
    except Exception as error:
        st.error(f"Failed to load history: {error}")


def send_research_query(query: str, session_id: str):
    """Send research query to backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/research/query",
            json={"query": query, "session_id": session_id},
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed: {response.status_code}"}
    except Exception as error:
        return {"error": str(error)}


def get_sessions_list():
    """Get list of all sessions."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/v1/sessions/list",
            params={"limit": 20}
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []


def create_new_session(title: str = "New Research Session"):
    """Create a new session."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/sessions/create",
            params={"title": title}
        )
        if response.status_code == 200:
            return response.json()["session_id"]
    except Exception as error:
        st.error(f"Failed to create session: {error}")
    return None


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Intelligent Research Assistant",
        page_icon="🔬",
        layout="wide"
    )
    
    init_session_state()
    
    # Title
    st.title("🔬 Intelligent Research Assistant")
    st.markdown("Multi-Agent AI System for Comprehensive Research")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Backend health
        backend_healthy = check_backend_health()
        if backend_healthy:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
            st.stop()
        
        st.divider()
        
        # Session Management
        st.header("📚 Sessions")
        
        # New session button
        if st.button("➕ New Session", use_container_width=True):
            title = f"Research Session {datetime.now().strftime('%m/%d %H:%M')}"
            new_session_id = create_new_session(title)
            if new_session_id:
                st.session_state.session_id = new_session_id
                st.session_state.messages = []
                st.success("New session created!")
                st.rerun()
        
        # Get current session
        if not st.session_state.session_id:
            st.session_state.session_id = get_active_session()
        
        # Display current session
        if st.session_state.session_id:
            st.info(f"**Active:** {st.session_state.session_id[-15:]}")
        
        st.divider()
        
        # Recent sessions
        st.subheader("Recent Sessions")
        sessions = get_sessions_list()
        
        for session in sessions[:5]:
            col1, col2 = st.columns([3, 1])
            with col1:
                session_label = session.get("title", "Session")[:30]
                if st.button(
                    f"📝 {session_label}", 
                    key=session["session_id"],
                    use_container_width=True
                ):
                    st.session_state.session_id = session["session_id"]
                    load_session_history(session["session_id"])
                    st.rerun()
            with col2:
                st.caption(f"{session.get('message_count', 0)} msgs")
        
        st.divider()
        
        # Information
        st.header("ℹ️ About")
        st.markdown("""
        **Research Agent**: Gathers information from arXiv, web, and documents
        
        **Summarizer Agent**: Organizes and condenses findings
        
        **Analyst Agent**: Provides insights and answers
        
        **Sources**: arXiv papers, Web (Perplexity), Your uploaded documents
        """)
    
    # Main chat interface
    st.header("💬 Research Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            with st.chat_message(role):
                st.markdown(content)
                
                # Show sources for assistant messages
                if role == "assistant" and message.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in message["sources"][:5]:
                            if source:
                                st.markdown(f"- {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask a research question..."):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from backend
        with st.chat_message("assistant"):
            with st.spinner("🤔 Researching... This may take a minute..."):
                response = send_research_query(prompt, st.session_state.session_id)
                
                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    answer = response.get("answer", "No response generated.")
                    sources = response.get("sources", [])
                    processing_time = response.get("processing_time", 0)
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Display metadata
                    st.caption(f"⏱️ Processing time: {processing_time:.2f}s")
                    
                    # Display sources
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources[:5]:
                                if source:
                                    st.markdown(f"- {source}")
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "timestamp": datetime.now().isoformat(),
                        "sources": sources
                    })


if __name__ == "__main__":
    main()
