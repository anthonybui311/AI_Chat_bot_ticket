import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List
import os
from dotenv import load_dotenv

# LangChain imports
from langchain_groq import ChatGroq 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain_core.messages import HumanMessage, AIMessage 
from pydantic import SecretStr
    
# Internal imports
import working.configuration.config as config
import working.backend.creating_part.create as create_module
import working.backend.editing_part.edit as edit_module
import working.backend.api_call as api

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure module logger
logger = logging.getLogger(__name__)
logger.debug(f"GROQ API Key loaded: {'Present' if GROQ_API_KEY else 'Missing'}")

# =====================================================
# STAGE MANAGEMENT CLASS
# =====================================================

class StageManager:
    """
    OPTIMIZED: Comprehensive stage management system
    Manages workflow stages, context switching, and state persistence.
    Handles transitions between different conversation stages.
    """
    
    # Stage constants for better maintainability
    STAGE_MAIN = "main"
    #Stages for creating ticket
    STAGE_CREATE = "create"
    STAGE_CONFIRMATION = "confirmation"
    STAGE_UPDATE_CONFIRMATION = "update_confirmation"
    STAGE_CORRECT = "correct"
    STAGE_ONE_CI_DATA = "1_ci_data"
    STAGE_MULTIPLE_CI_DATA = "multiple_ci_data"
    #Stages for editing ticket
    STAGE_EDIT = "edit"
    STAGE_UPDATING_TICKET = "updating_ticket"
    STAGE_EDIT_CONFIRMATION = "edit_confirmation"


    def __init__(self):
        """Initialize stage manager with default state"""
        self.current_stage = self.STAGE_MAIN
        self.previous_stage = None
        self.stage_contexts = self._initialize_stage_contexts()
        self.pending_ticket_data = None
        self.pending_ci_data = None
        self.stage_history = [self.STAGE_MAIN]
        logger.info(f"StageManager initialized with stage: {self.current_stage}")

    def _initialize_stage_contexts(self) -> Dict[str, str]:
        """Initialize stage contexts from config"""
        return {
            self.STAGE_MAIN: config.CONTEXT,
            self.STAGE_CREATE: config.CREATE_CONTEXT,
            self.STAGE_EDIT: config.EDIT_CONTEXT,
            self.STAGE_CONFIRMATION: config.CONFIRMATION_CONTEXT,
            self.STAGE_UPDATE_CONFIRMATION: config.UPDATE_CONFIRMATION_CONTEXT,
            self.STAGE_CORRECT: config.CORRECT_CONTEXT,
            self.STAGE_ONE_CI_DATA: config.ONE_CI_DATA_CONTEXT,
            self.STAGE_MULTIPLE_CI_DATA: config.MULTIPLE_CI_DATA_CONTEXT,
            self.STAGE_UPDATING_TICKET: config.UPDATING_TICKET_CONTEXT,
            self.STAGE_EDIT_CONFIRMATION: config.EDIT_CONFIRMATION_CONTEXT
        }

    def get_current_context(self) -> str:
        """Get context for current stage"""
        context = self.stage_contexts.get(self.current_stage, config.CONTEXT)
        logger.debug(f"Retrieved context for stage: {self.current_stage}")
        return context

    def switch_stage(self, new_stage: str) -> bool:
        """
        OPTIMIZED: Switch to new stage with validation and logging
        Args:
            new_stage: Target stage name
        Returns:
            True if switch successful, False otherwise
        """
        if new_stage not in self.stage_contexts:
            logger.error(f"Invalid stage transition attempted: {new_stage}")
            return False

        self.previous_stage = self.current_stage
        self.current_stage = new_stage
        self.stage_history.append(new_stage)
        logger.info(f"Stage transition: {self.previous_stage} → {new_stage}")
        return True

    def go_back_stage(self) -> bool:
        """Go back to previous stage if available"""
        if self.previous_stage and self.previous_stage in self.stage_contexts:
            return self.switch_stage(self.previous_stage)
        return False

    def reset_to_main(self) -> None:
        """Reset to main stage and clear data"""
        self.switch_stage(self.STAGE_MAIN)
        self.clear_ticket_data()
        self.clear_ci_data()
        logger.info("Reset to main stage")

    # Stage checking methods
    def is_in_main_stage(self) -> bool:
        """Check if currently in main stage"""
        return self.current_stage == self.STAGE_MAIN

    def is_in_confirmation_stage(self) -> bool:
        """Check if currently in confirmation stage"""
        return self.current_stage == self.STAGE_CONFIRMATION

    def is_in_correct_stage(self) -> bool:
        """Check if currently in correct stage"""
        return self.current_stage == self.STAGE_CORRECT

    # Ticket data management
    def store_ticket_data(self, ticket_data: Dict[str, Any]) -> None:
        """Store ticket data for later use"""
        self.pending_ticket_data = ticket_data.copy()
        logger.info(f"Stored ticket data: {list(ticket_data.keys())}")

    def get_stored_ticket_data(self) -> Optional[Dict[str, Any]]:
        """Get stored ticket data"""
        return self.pending_ticket_data.copy() if self.pending_ticket_data else {}
    def clear_ticket_data(self) -> None:
        """Clear stored ticket data"""
        self.pending_ticket_data = None
        logger.info("Cleared stored ticket data")

    # CI data management
    def store_ci_data(self, ci_data: List[Dict[str, Any]]) -> None:
        """Store CI data for later use"""
        self.pending_ci_data = ci_data.copy()
        logger.info(f"Stored CI data: {len(ci_data)} records")

    def get_stored_ci_data(self) -> Optional[List[Dict[str, Any]]]:
        """Get stored CI data"""
        return self.pending_ci_data.copy() if self.pending_ci_data else None

    def clear_ci_data(self) -> None:
        """Clear stored CI data"""
        self.pending_ci_data = None
        logger.info("Cleared stored CI data")

# =====================================================
# CHAT HISTORY CLASS
# =====================================================

class ChatHistory:
    """
    OPTIMIZED: Enhanced chat history management
    Handles conversation history with persistent storage,
    session management, and message formatting.
    """

    def __init__(self):
        """Initialize chat history with session file"""
        self.messages: List[Any] = []
        self.session_filename = self._create_session_filename()
        self.session_file_path = f"{config.DATA_PATH}/{self.session_filename}"
        self._initialize_session_file()
        logger.info(f"ChatHistory initialized: {self.session_filename}")

    def _create_session_filename(self) -> str:
        """Create unique session filename"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"chat_{timestamp}.txt"

    def _initialize_session_file(self) -> None:
        """Initialize session file with header"""
        try:
            with open(self.session_file_path, "w", encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("AI TICKET SUPPORT CHATBOT - CHAT SESSION\n")
                f.write("=" * 60 + "\n")
                f.write(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
            logger.info(f"Session file initialized: {self.session_file_path}")
        except Exception as e:
            logger.error(f"Failed to initialize session file: {e}")
            raise

    def add_user_message(self, message: str) -> None:
        """Add user message to history and file"""
        try:
            self.messages.append(HumanMessage(content=message))
            self._append_message_to_file("USER", message)
            logger.debug("User message added to history")
        except Exception as e:
            logger.error(f"Failed to add user message: {e}")

    def add_ai_message(self, message: str) -> None:
        """Add AI message to history and file"""
        try:
            self.messages.append(AIMessage(content=message))
            self._append_message_to_file("AI", message)
            logger.debug("AI message added to history")
        except Exception as e:
            logger.error(f"Failed to add AI message: {e}")

    def _append_message_to_file(self, sender: str, message: str) -> None:
        """Append message to session file"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            with open(self.session_file_path, "a", encoding='utf-8') as f:
                f.write(f"[{timestamp}] {sender}: {message}\n\n")
        except Exception as e:
            logger.error(f"Failed to write to session file: {e}")

    def get_messages(self) -> List[Any]:
        """Get all messages in history"""
        return self.messages.copy()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary statistics"""
        user_messages = sum(1 for msg in self.messages if isinstance(msg, HumanMessage))
        ai_messages = sum(1 for msg in self.messages if isinstance(msg, AIMessage))
        return {
            "total_messages": len(self.messages),
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "session_file": self.session_filename
        }

# =====================================================
# LANGCHAIN INTEGRATION FUNCTIONS
# =====================================================

def create_chat_prompt() -> ChatPromptTemplate:
    """Create optimized chat prompt template"""
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        logger.debug("Chat prompt template created")
        return prompt
    except Exception as e:
        logger.error(f"Failed to create chat prompt: {e}")
        raise

def create_llm() -> ChatGroq:
    """Create optimized LLM instance with error handling"""
    try:
        # Convert API key to SecretStr if it exists
        api_key = SecretStr(GROQ_API_KEY) if GROQ_API_KEY else None
        
        # Create kwargs dict with only supported parameters
        kwargs = {
            "model": config.MODEL_NAME,
            "temperature": config.TEMPERATURE,
            "max_tokens": config.MAX_TOKENS,
            "timeout": 30
        }
        
        # Only add api_key if it exists
        if api_key:
            kwargs["api_key"] = api_key
            
        # Initialize with explicit parameters
        llm = ChatGroq(**kwargs)
        logger.debug(f"LLM created: {config.MODEL_NAME}")
        return llm
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        raise

def create_chain():
    """Create optimized LangChain processing chain"""
    try:
        prompt = create_chat_prompt()
        llm = create_llm()
        chain = prompt | llm
        logger.info("LangChain processing chain created successfully")
        return chain
    except Exception as e:
        logger.error(f"Failed to create chain: {e}")
        raise

# =====================================================
# RESPONSE PROCESSING FUNCTIONS
# =====================================================

def get_response(chain, chat_history: ChatHistory, question: str, context: str = "") -> Tuple[str, str]:
    """
    OPTIMIZED: Get response from AI with enhanced error handling
    Args:
        chain: LangChain processing chain
        chat_history: Chat history object
        question: User's question
        context: Additional context
    Returns:
        Tuple of (response_data, summary)
    """
    try:
        chain_input = {
            "question": question,
            "context": context,
            "chat_history": chat_history.get_messages()
        }

        # Process through chain
        response = chain.invoke(chain_input)
        content = response.content if hasattr(response, 'content') else str(response)

        # Parse JSON response
        try:
            result = json.loads(content)
            response_field = result.get("response", "")
            summary = result.get("summary", "error")
            logger.debug(f"AI Response processed - Summary: {summary}")
            return response_field, summary

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}")
            error_message = "Xin lỗi, có lỗi xảy ra khi xử lý phản hồi. Vui lòng thử lại."
            return error_message, "json_error"

    except Exception as e:
        logger.error(f"Chain invoke failed: {e}")
        error_message = f"Xin lỗi, có lỗi xảy ra: {e}"
        return error_message, "error"

#TODO: fix this for the edit stage
def route_to_stage(stage_manager: StageManager, response_text, summary: str,
                   user_input: str, chain, chat_history: ChatHistory) -> Tuple[str, str]:
    """
    OPTIMIZED: Enhanced stage routing with comprehensive workflow handling
    Args:
        stage_manager: Stage management object
        response_text: AI response
        summary: Response summary
        user_input: Original user input
        chain: LangChain chain
        chat_history: Chat history
    Returns:
        Tuple of (final_response, final_summary)
    """
    try:
        logger.info(f"Routing - Stage: {stage_manager.current_stage}, Summary: {summary}")

        # Route based on current stage
        if stage_manager.is_in_main_stage():
            return _handle_main_stage(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == 'create':
            return _handle_create_stage_routing(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == 'edit':
            return _handle_edit_stage_routing(stage_manager, response_text, summary)
        
        elif stage_manager.is_in_confirmation_stage():
            return create_module._handle_confirmation_stage(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == 'update_confirmation':
            return create_module._handle_update_confirmation_stage(stage_manager, response_text, summary)
        
        elif stage_manager.is_in_correct_stage():
            return create_module._handle_correct_stage(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == '1_ci_data':
            return create_module._handle_single_ci_data_stage(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == 'multiple_ci_data':
            return create_module._handle_multiple_ci_data_stage(stage_manager, response_text, summary)
        
        elif stage_manager.current_stage == 'updating_ticket':
            return edit_module.handle_updating_ticket_stage(stage_manager, response_text, summary)

        elif stage_manager.current_stage == 'edit_confirmation':  
            return edit_module.handle_edit_confirmation_stage(stage_manager, response_text, summary)


        # Fallback
        logger.warning(f"Unhandled stage: {stage_manager.current_stage}")
        return response_text, summary

    except Exception as e:
        logger.error(f"Error in route_to_stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra trong quá trình xử lý: {e}"
        return error_response, "error"

# =====================================================
# STAGE HANDLING FUNCTIONS
# =====================================================

def _handle_main_stage(stage_manager: StageManager, response_text, summary: str) -> Tuple[str, str]:
    """Handle main stage routing"""
    if summary == 'tạo ticket':
        stage_manager.switch_stage('create')
        return create_module.handle_create_stage(response_text, summary, stage_manager)
    elif summary == 'sửa ticket':
        stage_manager.switch_stage('edit')
        return edit_module.handle_edit_stage(response_text, summary, stage_manager)
    elif summary == 'thoát':
        return response_text, summary
    else:
        return response_text, summary

def _handle_create_stage_routing(stage_manager: StageManager, response_text, summary: str) -> Tuple[str, str]:
    """Handle create stage routing"""
    final_response, final_summary = create_module.handle_create_stage(
        response_text, summary, stage_manager
    )

    # Handle stage transitions
    if final_summary == "đúng" and stage_manager.get_stored_ticket_data():
        stage_manager.switch_stage('confirmation')
        return create_module._handle_confirmation_stage(stage_manager, final_response, final_summary)
    elif final_summary == "chờ xác nhận":
        stage_manager.switch_stage('confirmation')
        return final_response, final_summary
    elif final_summary in ['thoát', 'sửa ticket']:
        stage_manager.reset_to_main()
        return final_response, final_summary

    return final_response, final_summary

def _handle_edit_stage_routing(stage_manager: StageManager, response_text, summary: str) -> Tuple[str, str]:
    """Handle edit stage routing"""
    final_response, final_summary = edit_module.handle_edit_stage(response_text, summary, stage_manager)

    # Handle stage transitions
    if final_summary in ['thoát', 'tạo ticket']:
        stage_manager.reset_to_main()
        return final_response, final_summary

    return final_response, final_summary


# =====================================================
# SESSION MANAGEMENT FUNCTIONS
# =====================================================

def exit_chat(chat_history: ChatHistory) -> None:
    """
    OPTIMIZED: Handle graceful chat exit with summary
    """
    try:
        # Write session summary
        summary = chat_history.get_conversation_summary()
        with open(chat_history.session_file_path, "a", encoding='utf-8') as f:
            f.write("\n" + "="*60 + "\n")
            f.write("SESSION SUMMARY\n")
            f.write("="*60 + "\n")
            f.write(f"Total messages: {summary['total_messages']}\n")
            f.write(f"User messages: {summary['user_messages']}\n")
            f.write(f"AI messages: {summary['ai_messages']}\n")
            f.write(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n")

        logger.info(f"Chat session ended: {chat_history.session_filename}")

    except Exception as e:
        logger.error(f"Error during chat exit: {e}")
