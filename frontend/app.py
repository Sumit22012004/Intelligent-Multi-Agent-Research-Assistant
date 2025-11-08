"""
Simple Streamlit interface for the Research Assistant.
Phase 1: Basic chat interface with connection test.
"""

import streamlit as st
import httpx
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="wide"
)


def check_backend_connection():
    """Check if backend is running."""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Main application interface."""
    
    # Title
    st.title("🔬 Intelligent Research Assistant")
    st.markdown("*Multi-Agent AI-Powered Research Tool*")
    
    # Check backend status
    with st.sidebar:
        st.header("System Status")
        
        if check_backend_connection():
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
            st.info("Make sure the backend is running on port 8000")
        
        st.divider()
        st.info(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Main chat interface
    st.header("💬 Research Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your research..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response (placeholder for Phase 1)
        with st.chat_message("assistant"):
            response = "Hello! I'm your research assistant. Full functionality will be available after Phase 3. For now, I'm just testing the interface! 🚀"
            st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
    
    # Footer
    st.divider()
    st.caption("Phase 1: Foundation - Basic interface is ready!")


if __name__ == "__main__":
    main()

