import streamlit as st
import uuid
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from working.frontend.utils.api_client import APIClient

def current_chat():
    st.title("🤖 AI TICKET SUPPORT CHATBOT")
    
    # Initialize API client
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()
    
    api_client = st.session_state.api_client
    
    # Initialize session
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = {
            "role": "assistant",
            "content": "Chào mừng! Tôi là trợ lý hỗ trợ ticket. Bạn muốn sửa hay tạo ticket?\n\n*(Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện)*",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(welcome_msg)
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")
        
        # New Session button
        if st.button("🔄 Tạo chat mới"):
            # End current session
            api_client.reset_session()
            # Clear messages
            st.session_state.messages = []
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
                response, success = api_client.chat(prompt)
            
            if success:
                st.markdown(response)
                response_timestamp = datetime.now().strftime("%H:%M:%S")
                st.caption(f"*{response_timestamp}*")
                
                # Add AI response to messages
                ai_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": response_timestamp
                }
                st.session_state.messages.append(ai_message)
            else:
                st.error(response)
                # If it's an exit message, reset the session
                if "tạm biệt" in response.lower() or "thoát" in response.lower():
                    api_client.reset_session()
    
    # Display session info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Tin nhắn:** {len(st.session_state.messages)}")

if __name__ == "__main__":
    current_chat()
