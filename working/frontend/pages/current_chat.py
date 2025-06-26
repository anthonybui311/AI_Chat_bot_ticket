import streamlit as st
import uuid
from datetime import datetime
import sys
import os
import time

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from working.frontend.utils.api_client import APIClient

# Initialize session state at the module level
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

def create_welcome_message():
    """Create a welcome message with current timestamp"""
    return {
        "role": "assistant",
        "content": "Chào mừng! Tôi là trợ lý hỗ trợ ticket. Bạn muốn sửa hay tạo ticket?\n\n*(Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện)*",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

def create_new_session():
    """Create a new chat session with welcome message"""
    st.session_state.api_client.reset_session()
    st.session_state.messages = [create_welcome_message()]

def current_chat():
    st.title("🤖 AI TICKET SUPPORT CHATBOT")
    
    # Always ensure there's at least a welcome message
    if not st.session_state.messages:
        st.session_state.messages = [create_welcome_message()]
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")
        
        # New Session button
        if st.button("🔄 Tạo chat mới"):
            create_new_session()
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"*{message['timestamp']}*")
    
    # Chat input
    if prompt := st.chat_input("Nhập tin nhắn của bạn ở đây..."):
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"*{timestamp}*")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, success = st.session_state.api_client.chat(prompt)
            
            # Add AI response to messages
            response_timestamp = datetime.now().strftime("%H:%M:%S")
            ai_message = {
                "role": "assistant",
                "content": response,
                "timestamp": response_timestamp
            }
            st.session_state.messages.append(ai_message)
            
            # Display response
            st.markdown(response)
            st.caption(f"*{response_timestamp}*")
            
            # If success is False, it means the summary was 'thoát'
            if  not success:
                # Wait a moment to show the goodbye message
                time.sleep(1)
                # Create new session
                create_new_session()
                st.rerun()
    
    # Display session info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Tin nhắn:** {len(st.session_state.messages)}")

if __name__ == "__main__":
    current_chat()
