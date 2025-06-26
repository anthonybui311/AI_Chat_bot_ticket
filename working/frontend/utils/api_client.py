import requests
from typing import Dict, List, Tuple, Optional
import streamlit as st

class APIClient:
    """Client for interacting with the chatbot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, message: str) -> Tuple[str, bool]:
        """
        Send a message to the chatbot and get the response
        Returns: (response_text, success_flag)
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "session_id": self.session_id
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Update session ID
            self.session_id = data["session_id"]
            
            return data["response"], data["success"]
            
        except requests.RequestException as e:
            st.error(f"API Error: {str(e)}")
            return f"Error communicating with chatbot: {str(e)}", False
    
    def get_chat_history(self) -> List[Dict]:
        """Get chat history for current session"""
        if not self.session_id:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/chat/{self.session_id}/history")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching chat history: {e}")
            return []
    
    def end_session(self) -> bool:
        """End the current chat session"""
        if not self.session_id:
            return True
        
        try:
            response = requests.delete(f"{self.base_url}/chat/{self.session_id}")
            response.raise_for_status()
            self.session_id = None
            return True
        except requests.RequestException as e:
            st.error(f"Error ending session: {e}")
            return False
    
    def reset_session(self):
        """Reset the current session"""
        if self.session_id:
            self.end_session()
        self.session_id = None 