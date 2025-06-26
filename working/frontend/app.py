import streamlit as st
import os
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="AI TICKET SUPPORT CHATBOT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add branding to sidebar first
with st.sidebar:
    st.title("🤖 AI TICKET SUPPORT CHATBOT")
    st.markdown("---")

# Page navigation
pages = [
    st.Page("pages/current_chat.py", title="Current Chat", icon="💬"),
    st.Page("pages/about_us.py", title="About Us", icon="ℹ️"),
]

# Create navigation
pg = st.navigation(pages, position="sidebar", expanded=True)


# Run the selected page
pg.run()
