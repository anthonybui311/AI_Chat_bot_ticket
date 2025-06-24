import sys
import logging
from typing import Optional, Tuple
from datetime import datetime

# Internal imports
import working.backend.editing_part.edit as edit_module
import working.backend.creating_part.create as create_module
import working.backend.utils as utils
import working.configuration.config as config
import os
import logging


log_directory = config.LOG_DIRECTORY

# Ensure the directory exists

os.makedirs(log_directory, exist_ok=True)

logname = os.path.join(log_directory, f"chatbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
# Configure logging with custom location
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logname, mode='a'),  # Use your custom location
        # logging.StreamHandler() # Also log but to terminal
    ]
)
logger = logging.getLogger(__name__)



class ChatbotSession:
    """
    OPTIMIZED: Encapsulate chatbot session management
    Handles initialization, state management, and cleanup
    """
    
    def __init__(self):
        """Initialize chatbot session components"""
        try:
            self.chain = utils.create_chain()
            self.chat_history = utils.ChatHistory()
            self.stage_manager = utils.StageManager()
            self.is_running = True
            logger.info("Chatbot session initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize chatbot session: {e}")
            raise
    
    def display_welcome_message(self) -> None:
        """Display welcome message and system status"""
        print("\n" + "="*60)
        print("🤖 AI TICKET SUPPORT CHATBOT")
        print("="*60)
        print("Chào mừng! Tôi là trợ lý hỗ trợ ticket.")
        print("Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện.")
        print("="*60)
    
    def get_user_input(self) -> str:
        """
        Get user input with stage indicator
        Returns: User input string
        """
        try:
            stage_display = self.stage_manager.current_stage.upper()
            prompt = f"\n[{stage_display}] Bạn: "
            return input(prompt).strip()
            
        except KeyboardInterrupt:
            logger.info("User initiated keyboard interrupt")
            return "thoát"
        except EOFError:
            logger.info("EOF received from user")
            return "thoát"
    
    def should_exit(self, user_input: str) -> bool:
        """Check if user wants to exit"""
        exit_keywords = ['tạm biệt', 'thoát', 'bye', 'exit', 'quit']
        return user_input.lower() in exit_keywords
    
    def process_user_input(self, user_input: str) -> Tuple[str, str]:
        """
        OPTIMIZED: Process user input through the workflow system
        
        Args:
            user_input: User's message
            
        Returns:
            Tuple of (response, summary)
        """
        try:
            # Get context for current stage
            current_context = self.stage_manager.get_current_context()
            
            if (self.stage_manager.is_in_confirmation_stage() and self._is_update_request(user_input)):
                current_context = config.UPDATE_CONFIRMATION_CONTEXT
                
                
            # Process through AI chain
            response_text, summary = utils.get_response(
                chain=self.chain,
                chat_history=self.chat_history,
                question=user_input,
                context=current_context
            )
            
            # Route to appropriate stage handler
            final_response, final_summary = utils.route_to_stage(
                self.stage_manager, response_text, summary, 
                user_input, self.chain, self.chat_history
            )

            
            return final_response, final_summary
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            error_response = f"Xin lỗi, có lỗi xảy ra: {e}. Vui lòng thử lại."
            return error_response, "error"
    
    def _is_update_request(self, user_input: str) -> bool:
        """Check if input is an update request"""
        update_keywords = ['cập nhật', 'sửa', 'thay đổi', 'đổi', 'chỉnh sửa', 'thành']
        return any(keyword in user_input.lower() for keyword in update_keywords)
    
    def display_response(self, response: str) -> None:
        """Display chatbot response with formatting"""
        print(f"\nChatbot: {response}")
    
    def handle_special_response(self, response: str, summary: str) -> bool:
        """
        Handle special response cases that require immediate action
        
        Returns:
            True if special case handled, False otherwise
        """
        if summary == 'thoát':
            self.chat_history.add_ai_message(response)
            self.display_response(response)
            self._shutdown()
            return True
            
        elif summary == 'ticket đã được tạo':
            self.chat_history.add_ai_message(response)
            self.display_response(response)
            
            # Reset to main stage after ticket creation
            if self.stage_manager.current_stage == 'correct':
                self.stage_manager.switch_stage('main')
                print("\n✅ Bạn có thể tiếp tục sử dụng hệ thống hoặc nhập 'thoát' để kết thúc.")
            return True
            
        return False
    
    def update_chat_history(self, user_input: str, response: str) -> None:
        """Update chat history with user input and response"""
        self.chat_history.add_user_message(user_input)
        self.chat_history.add_ai_message(response)
    
    def _shutdown(self) -> None:
        """Handle graceful shutdown"""
        try:
            utils.exit_chat(self.chat_history)
            self.is_running = False
            logger.info("Chatbot session ended gracefully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def run(self) -> None:
        """
        OPTIMIZED: Main conversation loop
        Cleaner structure with better error handling
        """
        self.display_welcome_message()
        
        while self.is_running:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Check for exit condition
                if self.should_exit(user_input):
                    self._shutdown()
                    break
                
                # Process user input
                response, summary = self.process_user_input(user_input)
                
                # Handle special cases
                if self.handle_special_response(response, summary):
                    continue
                
                # Update chat history and display response
                self.update_chat_history(user_input, response)
                self.display_response(response)
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Cuộc trò chuyện bị ngắt bởi người dùng.")
                self._shutdown()
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"❌ Lỗi không mong muốn: {e}")
                print("Vui lòng thử lại hoặc nhập 'thoát' để kết thúc.")


def start() -> None:
    """
    OPTIMIZED: Main entry point with proper error handling
    """
    try:
        session = ChatbotSession()
        session.run()
        
    except KeyboardInterrupt:
        print("\n\nChương trình bị ngắt bởi người dùng.")
        sys.exit(0)
        
    except Exception as e:
        logger.critical(f"Critical error in main: {e}")
        print(f"❌ Lỗi nghiêm trọng: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    start()
