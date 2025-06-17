<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Hướng Dẫn Chi Tiết Xây Dựng AI Chatbot với LangChain + GROQ API

## Phân Tích Kiến Trúc Hệ Thống Hiện Tại

Dựa vào sơ đồ hệ thống trong file PDF và code hiện tại, hệ thống của bạn là một chatbot hỗ trợ tạo và sửa ticket với workflow rõ ràng. Mỗi component có vai trò riêng biệt trong kiến trúc tổng thể [^1][^2].

### Components Chính Trong Kiến Trúc

1. **User Interface**: Hiện tại là CLI-based (qua file start.py), sẽ được nâng cấp thành web-based [^3][^4]
2. **Backend Logic**: Phân chia theo chức năng (tạo ticket, sửa ticket) [^5][^6]
3. **AI Core**: Hiện tại sử dụng LangChain với GROQ API để phân tích ý định và xử lý câu hỏi [^7][^8]
4. **Database**: Chưa có implementation, hiện đang lưu conversation vào file text [^6][^7]
5. **External API**: Tương tác với hệ thống CA SMD để quản lý ticket [^1][^9]

### Cách LangChain + GROQ Fit Vào Kiến Trúc

LangChain đóng vai trò làm "brain" của chatbot, xử lý input từ người dùng, phân tích ý định, và tạo response phù hợp. GROQ API cung cấp mô hình ngôn ngữ lớn với khả năng xử lý nhanh và chi phí hợp lý [^2][^3].

Hiện tại trong file utils.py, LangChain đã được implement cơ bản với GROQ, nhưng chưa có cấu trúc rõ ràng cho memory management, error handling và integration với database [^7][^10].

## Review Code Hiện Tại

### Điểm Mạnh

1. **Kiến trúc modular**: Code được tách thành các module riêng biệt (start.py, create.py, utils.py, config.py) [^5][^6][^7][^8]
2. **LangChain integration**: Đã implement cơ bản LangChain với GROQ trong utils.py [^7][^11]
3. **Context management**: Sử dụng context trong config.py để điều chỉnh behavior của AI [^8][^3]
4. **Error handling cơ bản**: Đã implement try-catch blocks [^5][^7]

### Điểm Cần Cải Thiện

1. **Thiếu database integration**: Hiện chỉ lưu chat history vào file text [^7][^12]
2. **Chưa có REST API**: Cần chuyển từ CLI sang web-based application [^5][^13]
3. **Memory management chưa tối ưu**: Cần implement advanced memory patterns cho context dài [^10][^14]
4. **Thiếu security measures**: Cần bổ sung authentication, rate limiting, và bảo vệ API keys [^15][^16]
5. **Error handling chưa đầy đủ**: Cần bổ sung comprehensive error handling cho AI failures [^7][^13]

## Implementation Guide Chi Tiết

### BƯỚC 1: Setup Environment \& Project Structure (Tuần 1)

```
# Cài đặt Python 3.11+ (phiên bản mới nhất được khuyến nghị)
# Tạo virtual environment
python -m venv chatbot_env
# Activate environment
source chatbot_env/bin/activate  # Linux/Mac
chatbot_env\Scripts\activate     # Windows
```


#### Cài đặt dependencies:

```
pip install fastapi==0.110.0 uvicorn==0.27.1 pydantic==2.6.3 python-dotenv==1.0.1 langchain==0.1.9 langchain-groq==0.1.5 sqlalchemy==2.0.28 asyncpg==0.29.0 redis==5.0.2 pytest==8.0.2 python-jose==3.3.0 passlib==1.7.4 python-multipart==0.0.7
```


#### Project Structure mới:

```
ticket_chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat API endpoints
│   │   └── ticket.py           # Ticket API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # App configuration
│   │   └── security.py         # Authentication logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── langchain_service.py # AI core logic (từ utils.py)
│   │   ├── ticket_service.py    # Ticket logic (từ create.py)
│   │   └── conversation_service.py # Chat management
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py         # SQLAlchemy models
│   └── utils/
│       ├── __init__.py
│       └── logging.py          # Logging configuration
├── alembic/                    # Database migrations
├── tests/
│   ├── __init__.py
│   └── test_chat.py
├── .env                        # Environment variables
└── requirements.txt            # Project dependencies
```


#### Migration từ code hiện tại:

- **start.py** → app/main.py + routers/
- **create.py** → services/ticket_service.py
- **utils.py** → services/langchain_service.py + services/conversation_service.py
- **config.py** → core/config.py
- **logging.py** → utils/logging.py [^9][^17][^18]


### BƯỚC 2: Database Schema Design (Tuần 2)

Tạo file app/models/database.py với các models sau [^12][^19]:

```python
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    tickets = relationship("Ticket", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # 'user' hoặc 'assistant'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    serial_number = Column(String(100))
    device_type = Column(String(100))
    problem_description = Column(Text)
    status = Column(String(50))
    external_ticket_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="tickets")
```

Tạo file app/core/database.py để quản lý database connection [^20][^19]:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```


### BƯỚC 3: Setup Configuration (Tuần 2)

Tạo file app/core/config.py [^8][^21]:

```python
import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Ticket Chatbot"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/chatbot")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # GROQ
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
    TEMPERATURE: float = 0.5
    
    # Path settings
    DATA_PATH: str = os.getenv("DATA_PATH", "data")
    
    # Prompt templates (migrate from existing config.py)
    CONTEXT: str = """
    BẠN LÀ MỘT AI CHATBOT QUẢN LÝ TICKET - NHẬN DIỆN Ý ĐỊNH
    
    VAI TRÒ
    Bạn là một AI chatbot chuyên quản lý ticket hỗ trợ kỹ thuật với khả năng nhận diện ý định người dùng.
    
    ĐỊNH DẠNG PHẢN HỒI
    QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có markdown, không có giải thích, không có văn bản nào khác.
    
    NHIỆM VỤ CHÍNH
    1. Phân tích tin nhắn của người dùng
    2. Xác định ý định chính
    3. Trả lời phù hợp và chuyển hướng đúng chức năng
    """
    
    CREATE_CONTEXT: str = """
    !!! CRITICAL INSTRUCTION - READ FIRST !!!
    BẠN PHẢI TUÂN THỦ NGHIÊM NGẶT: CHỈ TRẢ VỀ JSON, KHÔNG BAO GIỜ TRẢ VỀ TEXT THÔNG THƯỜNG
    """
    
    EDIT_CONTEXT: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

Tạo file .env trong thư mục gốc:

```
# API
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/chatbot_db

# Redis
REDIS_URL=redis://localhost:6379/0

# GROQ
GROQ_API_KEY=your-groq-api-key-here
MODEL_NAME=llama-3.1-8b-instant
TEMPERATURE=0.5

# Paths
DATA_PATH=./data
```


### BƯỚC 4: LangChain + GROQ Integration (Tuần 3)

Tạo file app/services/langchain_service.py (nâng cấp từ utils.py) [^2][^3][^11]:

```python
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings
import json
from typing import List, Dict, Any, Optional
import logging
import time
import redis

# Setup Redis client for caching
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
CACHE_TTL = 3600  # 1 hour cache expiry

class LangchainService:
    def __init__(self):
        self.llm = self._create_llm()
        self.parser = JsonOutputParser()
    
    def _create_llm(self):
        """Tạo LLM instance với error handling và retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return ChatGroq(
                    model_name=settings.MODEL_NAME,
                    temperature=settings.TEMPERATURE,
                    groq_api_key=settings.GROQ_API_KEY
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    logging.error(f"Failed to initialize LLM after {max_retries} attempts: {e}")
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def create_chain(self, context: str = ""):
        """Tạo chain xử lý với context nhất định"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        return (
            {
                "context": lambda x: context or settings.CONTEXT,
                "chat_history": lambda x: x.get("chat_history", []),
                "question": lambda x: x.get("question", "")
            }
            | prompt
            | self.llm
            | self.parser
        )
    
    def get_response(self, 
                     question: str, 
                     chat_history: List[Dict[str, Any]], 
                     context: str = "",
                     use_cache: bool = True):
        """
        Xử lý câu hỏi và trả về response từ AI, với caching và error handling
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = f"chat:{hash(str(chat_history))}{hash(question)}{hash(context)}"
            cached = redis_client.get(cache_key)
            if cached:
                logging.info("Cache hit, returning cached response")
                return json.loads(cached)
        
        # Create a fresh chain (LLMs should be stateless)
        chain = self.create_chain(context)
        
        # Process input with error handling
        try:
            response = chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            
            # Cache successful response
            if use_cache:
                redis_client.setex(
                    cache_key,
                    CACHE_TTL,
                    json.dumps(response)
                )
            
            return response
        except Exception as e:
            logging.error(f"Error in AI response generation: {e}")
            # Return graceful error response
            return {
                "response": f"Xin lỗi, có lỗi xảy ra: {str(e)}",
                "summary": "system_error"
            }
```


### BƯỚC 5: Conversation Service (Tuần 3)

Tạo file app/services/conversation_service.py để quản lý conversation history [^10][^14][^20]:

```python
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import Conversation, Message, User
from datetime import datetime
import uuid

class ConversationService:
    @staticmethod
    async def create_conversation(db: Session, user_id: int, title: str = None) -> Conversation:
        """Tạo conversation mới"""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    async def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
        """Lấy conversation theo ID"""
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    @staticmethod
    async def add_message(db: Session, 
                         conversation_id: int, 
                         role: str, 
                         content: str) -> Message:
        """Thêm message vào conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    async def get_messages(db: Session, conversation_id: int) -> List[Message]:
        """Lấy tất cả message trong conversation"""
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
    
    @staticmethod
    async def get_conversation_history(db: Session, conversation_id: int) -> List[Dict[str, Any]]:
        """Lấy lịch sử conversation ở format phù hợp cho LangChain"""
        messages = await ConversationService.get_messages(db, conversation_id)
        history = []
        
        for msg in messages:
            if msg.role == "user":
                history.append({"type": "human", "content": msg.content})
            else:
                history.append({"type": "ai", "content": msg.content})
        
        return history
    
    @staticmethod
    async def get_user_conversations(db: Session, user_id: int) -> List[Conversation]:
        """Lấy tất cả conversation của user"""
        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
```


### BƯỚC 6: Ticket Service (Tuần 3)

Tạo file app/services/ticket_service.py (nâng cấp từ create.py) [^6]:

```python
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.orm import Session
from app.models.database import Ticket
import logging

class TicketService:
    @staticmethod
    async def create_ticket(db: Session, conversation_id: int, ticket_data: Dict[str, Any]) -> Tuple[bool, Optional[Ticket]]:
        """
        Tạo ticket mới từ dữ liệu được cung cấp
        Returns: (success, ticket_object)
        """
        try:
            # Validate ticket data
            valid, missing_fields = TicketService.validate_ticket_data(ticket_data)
            if not valid:
                logging.warning(f"Invalid ticket data. Missing fields: {missing_fields}")
                return False, None
            
            # Create ticket in database
            ticket = Ticket(
                conversation_id=conversation_id,
                serial_number=ticket_data.get("serial_number", ""),
                device_type=ticket_data.get("device_type", ""),
                problem_description=ticket_data.get("problem_description", ""),
                status="created"
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            # TODO: Integrate with external ticket system (CA SMD)
            # external_id = TicketService.submit_to_external_system(ticket)
            # if external_id:
            #     ticket.external_ticket_id = external_id
            #     db.commit()
            
            return True, ticket
        except Exception as e:
            db.rollback()
            logging.error(f"Error creating ticket: {e}")
            return False, None
    
    @staticmethod
    def validate_ticket_data(ticket_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate dữ liệu ticket
        Returns: (is_valid, missing_fields)
        """
        required_fields = ['serial_number', 'device_type', 'problem_description']
        missing_fields = []
        
        if not isinstance(ticket_data, dict):
            return False, required_fields
        
        for field in required_fields:
            if field not in ticket_data or not str(ticket_data.get(field, '')).strip():
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    async def update_ticket(db: Session, ticket_id: int, update_data: Dict[str, Any]) -> Tuple[bool, Optional[Ticket]]:
        """
        Cập nhật thông tin ticket
        """
        try:
            ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return False, None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(ticket, key):
                    setattr(ticket, key, value)
            
            db.commit()
            db.refresh(ticket)
            return True, ticket
        except Exception as e:
            db.rollback()
            logging.error(f"Error updating ticket: {e}")
            return False, None
    
    @staticmethod
    async def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Lấy thông tin ticket theo ID"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    async def get_tickets_by_conversation(db: Session, conversation_id: int) -> List[Ticket]:
        """Lấy tất cả ticket trong conversation"""
        return db.query(Ticket).filter(Ticket.conversation_id == conversation_id).all()
```


### BƯỚC 7: FastAPI API Setup (Tuần 4)

Tạo file app/main.py [^4][^13][^22]:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import chat, ticket, auth
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="Chatbot AI for ticket management",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(ticket.router, prefix=settings.API_V1_STR, tags=["ticket"])

@app.get("/")
async def root():
    return {"message": "Welcome to Ticket Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Create necessary directories
os.makedirs(settings.DATA_PATH, exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```


### BƯỚC 8: API Endpoints (Tuần 4)

Tạo file app/routers/chat.py [^4][^13]:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.langchain_service import LangchainService
from app.services.conversation_service import ConversationService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/chat")
langchain_service = LangchainService()

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str

class ConversationResponse(BaseModel):
    id: int
    title: str
    messages: List[MessageResponse]

@router.post("/conversations", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo conversation mới"""
    conversation = await ConversationService.create_conversation(db, user_id)
    return {"id": conversation.id, "title": conversation.title}

@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách conversations của user"""
    conversations = await ConversationService.get_user_conversations(db, user_id)
    return [{"id": conv.id, "title": conv.title, "updated_at": conv.updated_at} for conv in conversations]

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gửi message và nhận response từ AI"""
    # Kiểm tra conversation tồn tại và thuộc về user
    conversation = await ConversationService.get_conversation(db, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Lưu user message
    await ConversationService.add_message(db, conversation_id, "user", message.content)
    
    # Lấy lịch sử chat
    history = await ConversationService.get_conversation_history(db, conversation_id)
    
    # Gọi AI và lấy response
    ai_response = langchain_service.get_response(
        question=message.content,
        chat_history=history,
        context=""  # Có thể điều chỉnh context dựa trên tình huống
    )
    
    # Lưu AI response
    response_text = ai_response.get("response", "")
    intent = ai_response.get("summary", "")
    
    await ConversationService.add_message(db, conversation_id, "assistant", response_text)
    
    return {
        "response": response_text,
        "intent": intent
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin conversation và history"""
    conversation = await ConversationService.get_conversation(db, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await ConversationService.get_messages(db, conversation_id)
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
    }
```

Tạo file app/routers/ticket.py:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.ticket_service import TicketService
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/tickets")

class TicketCreate(BaseModel):
    conversation_id: int
    serial_number: str
    device_type: str
    problem_description: str

class TicketUpdate(BaseModel):
    serial_number: Optional[str] = None
    device_type: Optional[str] = None
    problem_description: Optional[str] = None
    status: Optional[str] = None

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tạo ticket mới"""
    success, ticket = await TicketService.create_ticket(
        db, 
        ticket_data.conversation_id,
        {
            "serial_number": ticket_data.serial_number,
            "device_type": ticket_data.device_type,
            "problem_description": ticket_data.problem_description
        }
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create ticket")
    
    return {
        "id": ticket.id,
        "serial_number": ticket.serial_number,
        "status": ticket.status
    }

@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin ticket"""
    success, ticket = await TicketService.update_ticket(
        db,
        ticket_id,
        ticket_data.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "id": ticket.id,
        "serial_number": ticket.serial_number,
        "device_type": ticket.device_type,
        "problem_description": ticket.problem_description,
        "status": ticket.status
    }

@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy thông tin ticket"""
    ticket = await TicketService.get_ticket(db, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "id": ticket.id,
        "serial_number": ticket.serial_number,
        "device_type": ticket.device_type,
        "problem_description": ticket.problem_description,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at
    }

@router.get("/conversation/{conversation_id}")
async def get_tickets_by_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách tickets trong conversation"""
    tickets = await TicketService.get_tickets_by_conversation(db, conversation_id)
    
    return [
        {
            "id": ticket.id,
            "serial_number": ticket.serial_number,
            "device_type": ticket.device_type,
            "problem_description": ticket.problem_description,
            "status": ticket.status
        }
        for ticket in tickets
    ]
```


### BƯỚC 9: Authentication \& Security (Tuần 5)

Tạo file app/core/security.py [^15][^16]:

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import User
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> int:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check if user exists
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return int(user_id)
```

Tạo file app/routers/auth.py:

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.database import User
from pydantic import BaseModel, EmailStr
from app.core.config import settings

router = APIRouter(prefix="/auth")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
```


### BƯỚC 10: Testing Setup (Tuần 5)

Tạo file tests/test_chat.py [^23][^24][^25]:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
import os
import sys

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_read_main():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Ticket Chatbot API"}

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.fixture
def test_token():
    """Create a test token"""
    # Register a test user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Try to register (may fail if user already exists)
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    
    assert response.status_code == 200
    return response.json()["access_token"]

def test_create_conversation(test_token):
    """Test creating a conversation"""
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/api/v1/chat/conversations", headers=headers)
    
    assert response.status_code == 201
    assert "id" in response.json()
    assert "title" in response.json()
    
    return response.json()["id"]

def test_send_message(test_token):
    """Test sending a message"""
    # Create a conversation first
    conversation_id = test_create_conversation(test_token)
    
    # Send a message
    headers = {"Authorization": f"Bearer {test_token}"}
    message_data = {"content": "Hello, I need help with a ticket"}
    
    response = client.post(
        f"/api/v1/chat/conversations/{conversation_id}/messages",
        json=message_data,
        headers=headers
    )
    
    assert response.status_code == 200
    assert "response" in response.json()
    assert "intent" in response.json()

def test_get_conversation(test_token):
    """Test retrieving a conversation"""
    # Create a conversation first
    conversation_id = test_create_conversation(test_token)
    
    # Get the conversation
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get(
        f"/api/v1/chat/conversations/{conversation_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()
    assert "messages" in response.json()

def test_create_ticket(test_token):
    """Test creating a ticket"""
    # Create a conversation first
    conversation_id = test_create_conversation(test_token)
    
    # Create a ticket
    headers = {"Authorization": f"Bearer {test_token}"}
    ticket_data = {
        "conversation_id": conversation_id,
        "serial_number": "SN12345",
        "device_type": "Máy in",
        "problem_description": "Không in được"
    }
    
    response = client.post(
        "/api/v1/tickets/",
        json=ticket_data,
        headers=headers
    )
    
    assert response.status_code == 201
    assert "id" in response.json()
    assert "serial_number" in response.json()
    assert "status" in response.json()
    
    return response.json()["id"]
```


### BƯỚC 11: Dockerization (Tuần 6)

Tạo file Dockerfile trong thư mục gốc [^26]:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Tạo file docker-compose.yml:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: always

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=chatbot_db
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```


### BƯỚC 12: Frontend Integration (Tuần 7-8)

Phần frontend có thể được phát triển riêng với React, Vue.js hoặc framework khác. API đã được thiết kế để tích hợp dễ dàng với frontend thông qua REST API endpoints.

## Roadmap Triển Khai

| Tuần | Nhiệm vụ | Chi tiết |
| :-- | :-- | :-- |
| 1 | Setup Environment \& Project Structure | Cài đặt môi trường, dependencies, tổ chức lại cấu trúc dự án |
| 2 | Database Schema \& Configuration | Thiết kế database schema, setup configuration files |
| 3 | LangChain + GROQ Integration \& Services | Implement core AI services, conversation và ticket management |
| 4 | FastAPI API Setup \& Endpoints | Xây dựng FastAPI app và API endpoints |
| 5 | Authentication \& Testing | Implement JWT auth và viết tests |
| 6 | Dockerization \& Deployment | Containerize app với Docker và chuẩn bị deployment |
| 7-8 | Frontend Development \& Integration | Xây dựng frontend và tích hợp với backend API |
| 9-10 | Testing \& Optimization | Comprehensive testing, performance tuning, và optimization |

## Best Practices \& Optimization

### API Key Management

- Luôn lưu API keys trong environment variables hoặc sử dụng service như Vault [^15][^16]
- Implement key rotation cho production environments
- Sử dụng .env file cho development và CI/CD secrets cho production


### Rate Limiting \& Cost Optimization

- Implement caching để giảm API calls đến GROQ [^27][^28][^29]
- Sử dụng batch processing để tối ưu calls [^27]
- Implement exponential backoff cho API calls thất bại [^27][^29]
- Theo dõi token usage để optimize costs [^27]


### Error Handling

- Implement comprehensive error handling với try-except blocks [^7][^13]
- Cung cấp error messages thân thiện với người dùng
- Log errors với chi tiết để troubleshooting [^9]
- Implement circuit breakers cho external API calls [^27]


### Testing

- Viết unit tests cho mỗi component [^23][^24][^25]
- Implement integration tests cho API endpoints [^23][^30]
- Sử dụng mocking để test AI components không cần gọi GROQ API thật [^23][^25]


### Performance Tuning

- Implement database indexes cho queries phổ biến [^12][^19]
- Sử dụng caching cho responses phổ biến [^27][^28]
- Implement async processing cho heavy tasks [^4][^13]


## Resources \& Documentation

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [GROQ API Documentation](https://console.groq.com/docs/quickstart)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [pytest Documentation](https://docs.pytest.org/)


## Kết Luận

Với hướng dẫn implementation này, bạn có thể nâng cấp từ code CLI hiện tại thành một hệ thống chatbot hoàn chỉnh với database persistence, REST API, caching, và security measures. Cấu trúc modular giúp dễ dàng mở rộng và bảo trì hệ thống trong tương lai.

Mỗi bước trong guide đã được thiết kế để có thể follow một cách dễ dàng, với các best practices và code examples đầy đủ. Bạn có thể tùy chỉnh các phần khác nhau dựa trên nhu cầu cụ thể của dự án.

<div style="text-align: center">⁂</div>

[^1]: So-do-kich-ban-Ho-tro-ticket.pdf

[^2]: https://www.byteplus.com/en/topic/448585

[^3]: https://www.byteplus.com/en/topic/448578

[^4]: https://www.koyeb.com/tutorials/use-mistralai-fastapi-and-fastui-to-build-a-conversational-ai-chatbot

[^5]: start.py

[^6]: create.py

[^7]: utils.py

[^8]: config.py

[^9]: logging.py

[^10]: https://dev.to/jamesbmour/langchain-part-4-leveraging-memory-and-storage-in-langchain-a-comprehensive-guide-h4m

[^11]: https://pypi.org/project/langchain-groq/

[^12]: https://dba.stackexchange.com/questions/268388/chat-conversation-history-entity-relationship-diagram

[^13]: https://dev.to/vipascal99/building-a-full-stack-ai-chatbot-with-fastapi-backend-and-react-frontend-51ph

[^14]: https://dev.to/jamesli/langchain-memory-components-in-depth-analysis-workflow-and-source-code-dissection-2an4

[^15]: https://escape.tech/blog/how-to-secure-fastapi-api/

[^16]: https://www.ficode.com/blog/everything-you-need-to-know-about-fastapi-security-with-jwt

[^17]: https://www.linkedin.com/pulse/fastapi-project-structure-best-practices-manikandan-parasuraman-fx4pc

[^18]: https://github.com/zhanymkanov/fastapi-best-practices

[^19]: https://aws.amazon.com/blogs/database/amazon-dynamodb-data-models-for-generative-ai-chatbots/

[^20]: https://blog.gopenai.com/implementing-session-based-chat-history-for-a-chatbot-using-langchain-and-database-cda0734f6344

[^21]: https://developer-service.blog/fastapi-best-practices-a-condensed-guide-with-examples/

[^22]: https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6

[^23]: https://betterstack.com/community/guides/testing/pytest-guide/

[^24]: https://blog.teclado.com/pytest-for-beginners/

[^25]: https://docs.pytest.org/en/stable/getting-started.html

[^26]: https://www.linkedin.com/pulse/building-your-first-fastapi-backend-application-parasuraman-5ozmc

[^27]: https://www.byteplus.com/en/topic/447736

[^28]: https://pypi.org/project/fastapi-redis-cache/

[^29]: https://www.byteplus.com/en/topic/448356

[^30]: https://www.kdnuggets.com/beginners-guide-unit-testing-python-code-pytest

[^31]: https://www.dataquest.io/blog/a-complete-guide-to-python-virtual-environments/

[^32]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

[^33]: https://www.youtube.com/watch?v=Kt6QqGoAlvI

[^34]: https://www.linkedin.com/pulse/fastapi-best-practices-condensed-guide-examples-nuno-bispo-9pd2e

[^35]: https://www.jetbrains.com/help/aqua/managing-dependencies.html

[^36]: https://seenode.com/blog/manage-python-requirements-txt-with-pip-tools/

[^37]: https://python.langchain.com/docs/integrations/chat/groq/

[^38]: https://js.langchain.com/docs/integrations/chat/groq/

[^39]: https://github.com/spider-rs/web-crawling-guides/blob/main/langchain-groq.md

[^40]: https://community.openai.com/t/how-to-design-a-database-schema-for-ai-chatbot/1137912

[^41]: https://www.patternfly.org/patternfly-ai/chatbot/chatbot-conversation-history

[^42]: https://www.youtube.com/watch?v=BknT1D6Gkbg

[^43]: https://realpython.com/pytest-python-testing/

[^44]: https://www.linkedin.com/pulse/revolutionize-your-fastapi-application-robust-redis-cache-khan-9auqf

[^45]: https://blog.devops.dev/building-enterprise-python-microservices-with-fastapi-in-2025-3-10-project-setup-1113658c9f0e

[^46]: https://www.digitalocean.com/community/tutorials/create-fastapi-app-using-docker-compose

