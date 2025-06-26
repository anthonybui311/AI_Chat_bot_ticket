import streamlit as st

def about_us():
    st.title("ℹ️ About AI Ticket Support Chatbot")
    
    # Main description
    st.markdown("""
    ## 🤖 Welcome to AI Ticket Support Chatbot
    
    This is a sophisticated ticket management chatbot built with FastAPI and Streamlit, designed to provide 
    intelligent support for creating and managing technical support tickets with a focus on Vietnamese language support.
    """)
    
    # Features section
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎫 Ticket Management
        - Create new support tickets
        - Edit existing tickets
        - Track ticket status
        - Multi-stage ticket processing
        
        ### 💬 Chat Interface
        - Real-time AI conversation
        - Vietnamese language support
        - Context-aware responses
        - Session management
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Technical Architecture
        - FastAPI backend
        - Streamlit frontend
        - RESTful API integration
        - Stateful session handling
        
        ### 🎯 User Experience
        - Clean, intuitive interface
        - Real-time responses
        - Error handling
        - Multi-stage conversations
        """)
    
    # AI Model Information
    st.subheader("🧠 AI Model & Processing")
    st.markdown("""
    The chatbot uses a sophisticated processing pipeline:
    
    - **Stage Management**: Handles different conversation stages (Main, Create, Edit, etc.)
    - **Context Awareness**: Maintains conversation context across messages
    - **Vietnamese NLP**: Optimized for Vietnamese language processing
    - **Error Recovery**: Graceful handling of various input scenarios
    - **Logging**: Comprehensive logging for debugging and monitoring
    """)
    
    # Technical Specifications
    st.subheader("⚙️ Technical Architecture")
    
    tech_specs = {
        "Backend Framework": "FastAPI",
        "Frontend Framework": "Streamlit",
        "API Protocol": "REST",
        "Language": "Python 3.8+",
        "Data Storage": "File-based (JSON)",
        "Session Management": "Server-side with FastAPI"
    }
    
    for key, value in tech_specs.items():
        st.markdown(f"- **{key}**: {value}")
    
    # Usage Instructions
    st.subheader("📖 Usage Instructions")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        1. **Create Ticket**: Start a conversation and follow the prompts to create a new ticket
        2. **Edit Ticket**: Use ticket ID to edit existing tickets
        3. **Exit Chat**: Type 'tạm biệt' or 'thoát' to end the conversation
        4. **New Session**: Click 'Tạo chat mới' to start a fresh conversation
        """)
    
    with st.expander("💡 Tips & Tricks"):
        st.markdown("""
        - **Ticket Creation**: Provide device serial number and issue description
        - **Editing**: Use clear ticket IDs when editing existing tickets
        - **Language**: The system is optimized for Vietnamese language
        - **Navigation**: Use the sidebar to access different features
        - **Error Messages**: Pay attention to error messages for guidance
        """)
    
    # Server Information
    st.subheader("🖥️ Server Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌐 Endpoints
        - **Frontend UI**: http://localhost:8501
        - **Backend API**: http://localhost:8000
        - **API Docs**: http://localhost:8000/docs
        - **Status**: Active when running
        """)
    
    with col2:
        st.markdown("""
        ### 🔄 Server Management
        - Start servers: `python main.py`
        - Stop servers: Press `Ctrl+C`
        - Auto-browser opening
        - Graceful shutdown handling
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with FastAPI & Streamlit | © 2024 AI Ticket Support Chatbot</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    about_us()
