import streamlit as st

def about_us():
    st.title("ℹ️ About AI Chatbot Assistant")
    
    # Main description
    st.markdown("""
    ## 🤖 Welcome to AI Chatbot Assistant
    
    This is a sophisticated multi-page chatbot application built with Streamlit, designed to provide 
    intelligent conversational AI capabilities with comprehensive chat history management.
    """)
    
    # Features section
    st.subheader("✨ Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💬 Current Chat
        - Real-time AI conversation
        - Message timestamps
        - Session management
        - Clear and save functionality
        
        ### 📚 Chat History
        - Persistent conversation storage
        - Search and filter capabilities
        - View and delete conversations
        - Export chat history
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Technical Features
        - Multi-page navigation
        - Session state management
        - File-based data persistence
        - Responsive design
        
        ### 🎯 User Experience
        - Clean, intuitive interface
        - Seamless page transitions
        - Professional styling
        - Error handling
        """)
    
    # AI Model Information
    st.subheader("🧠 AI Model Information")
    st.markdown("""
    This chatbot is powered by a custom AI model integrated through `start.py`. The model provides:
    
    - **Contextual Understanding**: Maintains conversation context across messages
    - **Multi-stage Processing**: Handles different conversation stages and workflows
    - **Error Handling**: Graceful handling of various input scenarios
    - **Logging**: Comprehensive logging for debugging and monitoring
    """)
    
    # Technical Specifications
    st.subheader("⚙️ Technical Specifications")
    
    tech_specs = {
        "Framework": "Streamlit",
        "Language": "Python 3.8+",
        "Data Storage": "JSON files",
        "Navigation": "st.navigation",
        "Chat Interface": "st.chat_input & st.chat_message",
        "Session Management": "st.session_state"
    }
    
    for key, value in tech_specs.items():
        st.markdown(f"- **{key}**: {value}")
    
    # Usage Instructions
    st.subheader("📖 Usage Instructions")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        1. **Start Chatting**: Navigate to the "Current Chat" page to begin a conversation
        2. **Save Conversations**: Use the "Save Chat" button to preserve important conversations
        3. **View History**: Access the "Chat History" page to review past conversations
        4. **Search**: Use the search functionality to find specific conversations
        5. **Export**: Download your chat history for backup or analysis
        """)
    
    with st.expander("💡 Tips & Tricks"):
        st.markdown("""
        - **Session Management**: Each chat session has a unique ID for tracking
        - **Timestamps**: All messages include timestamps for reference
        - **Search**: Search works on both conversation titles and message content
        - **Navigation**: Use the sidebar to switch between pages seamlessly
        - **Data Persistence**: All conversations are automatically saved locally
        """)
    
    # Version and Contact Information
    st.subheader("📞 Support & Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 Version Information
        - **Version**: 1.0.0
        - **Release Date**: 2025
        - **Last Updated**: June 2025
        - **Status**: Production Ready
        """)
    
    with col2:
        st.markdown("""
        ### 🔗 Useful Links
        - [Streamlit Documentation](https://docs.streamlit.io)
        - [Python Documentation](https://docs.python.org)
        - [GitHub Repository](#)
        - [Report Issues](#)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit | © 2025 AI Chatbot Assistant</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    about_us()
