import streamlit as st
import sys
import os
from typing import Dict, Any, Tuple
import logging

# Add your project path to import your modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
import working.backend.starting_part.start as start
import working.backend.utils as utils
import working.configuration.config as config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'stage_manager' not in st.session_state:
        # Initialize your stage manager here
        st.session_state.stage_manager = utils.StageManager()
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'main'

def main():
    st.set_page_config(
        page_title="Ticket Management Chatbot",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for controls
    create_sidebar()
    
    # Main chat interface
    create_chat_interface()

def create_sidebar():
    """Create sidebar with controls and information"""
    st.sidebar.title("🎫 Ticket Bot Controls")
    
    # Current stage display
    st.sidebar.info(f"Current Stage: {st.session_state.current_stage}")
    
    # Quick actions
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🆕 Create New Ticket"):
        handle_quick_action("tạo ticket")
    
    if st.sidebar.button("✏️ Edit Ticket"):
        handle_quick_action("sửa ticket")
    
    if st.sidebar.button("🔍 Search Ticket"):
        handle_quick_action("tìm ticket")
    
    if st.sidebar.button("🚪 Exit"):
        handle_quick_action("thoát")
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.stage_manager = utils.StageManager()
        st.session_state.current_stage = 'main'
        st.rerun()
    
    # Chat statistics
    st.sidebar.subheader("Chat Statistics")
    st.sidebar.metric("Messages", len(st.session_state.chat_history))
    
    # Help section
    with st.sidebar.expander("❓ Help"):
        st.write("""
        **Available Commands:**
        - "tạo ticket" - Create new ticket
        - "sửa ticket" - Edit existing ticket
        - "tìm ticket" - Search for tickets
        - "thoát" - Exit the system
        
        **Ticket Creation:**
        Provide device S/N or ID and issue description
        
        **Ticket Editing:**
        Provide ticket ID and specify what to update
        """)

def create_chat_interface():
    """Create the main chat interface"""
    st.title("🤖 Ticket Management Chatbot")
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        display_chat_history()
    
    # Input area
    create_input_area()

def display_chat_history():
    """Display the chat history with proper formatting"""
    if not st.session_state.chat_history:
        # Welcome message
        with st.chat_message("assistant"):
            st.markdown("""
            👋 **Chào mừng bạn đến với hệ thống quản lý ticket!**
            
            Tôi có thể giúp bạn:
            - 🆕 Tạo ticket mới
            - ✏️ Sửa ticket hiện có  
            - 🔍 Tìm kiếm ticket
            
            Hãy cho tôi biết bạn muốn làm gì!
            """)
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(message['content'])

def create_input_area():
    """Create the input area for user messages"""
    # Use columns for better layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.chat_input("Nhập tin nhắn của bạn...")
    
    if user_input:
        handle_user_input(user_input)

def handle_user_input(user_input: str):
    """Process user input and generate bot response"""
    try:
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Process the input through your existing chatbot logic
        response, summary = process_chatbot_input(user_input)
        
        # Add bot response to chat history
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response
        })
        
        # Update current stage
        st.session_state.current_stage = st.session_state.stage_manager.current_stage
        
        # Rerun to update the interface
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        st.error(f"Có lỗi xảy ra: {e}")

def process_chatbot_input(user_input: str) -> Tuple[str, str]:
    """Process input through your existing chatbot logic"""
    try:
        # Use your existing start.py logic
        response, summary = start.ChatbotSession().process_user_input(user_input)
        
        return response, summary
        
    except Exception as e:
        logger.error(f"Error in chatbot processing: {e}")
        return "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu của bạn.", "error"

def handle_quick_action(action: str):
    """Handle quick action buttons"""
    try:
        response, summary = process_chatbot_input(action)
        
        # Add both user action and bot response to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": f"*[Quick Action: {action}]*"
        })
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        st.session_state.current_stage = st.session_state.stage_manager.current_stage
        st.rerun()
        
    except Exception as e:
        logger.error(f"Error handling quick action: {e}")
        st.error(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()
