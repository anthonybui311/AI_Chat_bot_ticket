from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn

from working.backend.starting_part.start import ChatbotSession
from working.configuration import config

app = FastAPI(
    title="AI Ticket Support Chatbot API",
    description="API for managing ticket support conversations",
    version="1.0.0"
)

# Store active sessions
active_sessions: Dict[str, ChatbotSession] = {}

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    success: bool
    session_id: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return the response"""
    try:
        session_id = request.session_id
        
        # Create new session if none exists
        if not session_id or session_id not in active_sessions:
            session = ChatbotSession()
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            active_sessions[session_id] = session
        else:
            session = active_sessions[session_id]
        
        # Process message
        response, summary = session.process_user_input(request.message)
        
        # Update chat history
        session.update_chat_history(request.message, response)
        
        # Check if this is an exit message
        if summary == 'thoát':
            if session_id in active_sessions:
                del active_sessions[session_id]
            return ChatResponse(
                response=response,
                success=False,
                session_id=session_id
            )
        
        return ChatResponse(
            response=response,
            success=summary != 'error',
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{session_id}/history", response_model=List[Message])
async def get_chat_history(session_id: str):
    """Get chat history for a specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = active_sessions[session_id]
        messages = []
        for msg in session.chat_history.messages:
            messages.append(Message(
                role="user" if msg.is_user else "assistant",
                content=msg.content,
                timestamp=msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            ))
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/{session_id}")
async def end_session(session_id: str):
    """End a chat session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        del active_sessions[session_id]
        return {"message": "Session ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_api():
    """Start the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_api()