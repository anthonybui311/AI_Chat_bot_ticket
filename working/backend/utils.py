from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import json
import configuration.config as config
import backend.creating_part.create as create
import backend.editing_part.edit as edit

# --- STAGE MANAGER CLASS ---
class StageManager:
    """
    NEW CLASS: Quản lý trạng thái stage của hệ thống
    - Theo dõi stage hiện tại
    - Chuyển đổi context tương ứng
    - Duy trì trạng thái xuyên suốt session
    """
    def __init__(self):
        self.current_stage = "main"  # Các stage: main, create, edit
        self.stage_contexts = {
            "main": config.CONTEXT,
            "create": config.CREATE_CONTEXT,
            "edit": config.EDIT_CONTEXT
        }
    
    def get_current_context(self):
        """Lấy context cho stage hiện tại"""
        return self.stage_contexts.get(self.current_stage, config.CONTEXT)
    
    def switch_stage(self, new_stage):
        """Chuyển đổi sang stage mới"""
        if new_stage in self.stage_contexts:
            old_stage = self.current_stage
            self.current_stage = new_stage
            print(f"[DEBUG] Stage changed: {old_stage} -> {new_stage}")
            return True
        return False
    
    def is_in_main_stage(self):
        """Kiểm tra có đang ở main stage không"""
        return self.current_stage == "main"
    
# --- CHAT HISTORY CLASS ---
class ChatHistory:
    """
    Lưu trữ lịch sử hội thoại và tự động ghi vào file.
    Mỗi phiên hội thoại có file riêng với timestamp duy nhất.
    """
    def __init__(self):
        self.messages = []
        self.session_filename = self._create_session_filename()
        self._initialize_session_file()

    def _create_session_filename(self):
        """Tạo tên file duy nhất dựa trên thời gian hiện tại"""
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"chat_{timestamp}.txt"
        return filename

    def _initialize_session_file(self):
        """Khởi tạo file session và ghi header"""
        file_path = f"{config.DATA_PATH}/{self.session_filename}"
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(f"=== New Chat Session Started ===\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 40 + "\n\n")
        print(f"Cuộc trò chuyện mới đã bắt đầu. Đang lưu vào: {self.session_filename}")

    def add_user_message(self, message):
        """Thêm tin nhắn người dùng vào lịch sử và lưu ngay vào file"""
        self.messages.append(HumanMessage(content=message))
        self._append_message_to_file("Bạn", message)

    def add_ai_message(self, message):
        """Thêm tin nhắn AI vào lịch sử và lưu ngay vào file"""
        self.messages.append(AIMessage(content=message))
        self._append_message_to_file("AI", message)

    def _append_message_to_file(self, sender, message):
        """Ghi một tin nhắn vào cuối file session"""
        file_path = f"{config.DATA_PATH}/{self.session_filename}"
        with open(file_path, "a", encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] {sender}: {message}\n\n")

    def get_messages(self):
        """Lấy tất cả tin nhắn trong lịch sử (cần cho AI nhớ cuộc hội thoại)"""
        return self.messages

# --- PROMPT TEMPLATE FUNCTION ---
def create_chat_prompt():
    """
    Tạo template prompt cho AI chatbot với khả năng nhớ lịch sử hội thoại
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    return prompt

# --- LLM FUNCTION ---
def create_llm():
    """Khởi tạo mô hình AI Groq Llama 3 làm bộ não cho chatbot"""
    llm = ChatGroq(
        model_name=config.MODEL_NAME,
        temperature=config.TEMPERATURE
    )
    return llm

# --- CHAIN FUNCTION ---
def create_chain():
    """Tạo chuỗi xử lý chatbot: prompt -> llm"""
    prompt = create_chat_prompt()
    llm = create_llm()
    chain = prompt | llm
    return chain

# --- CHAT FUNCTION ---
def get_response(chain, chat_history, question, context=""):
    """
    Lấy phản hồi từ AI chatbot với khả năng xử lý 2 loại response
    
    Args:
        chain: Chuỗi xử lý LangChain
        chat_history: Đối tượng ChatHistory
        question: Câu hỏi của người dùng
        context: Ngữ cảnh bổ sung (tùy chọn)
    
    Returns:
        tuple: (response_data, summary) - Response data và summary
    """
    chain_input = {
        "question": question,
        "context": context,
        "chat_history": chat_history.get_messages()
    }
    
    try:
        response = chain.invoke(chain_input)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON output
        try:
            result = json.loads(content)
            print(f"Debug - Parsed JSON: {result}")
            print(f"Debug - Type of result: {type(result)}")
            
            # Extract response và summary
            response_field = result.get("response", "")
            print(f"Debug - Response field: {type(response_field)}")
            
            summary = result.get("summary", None)
            
            return response_field, summary
            
        except json.JSONDecodeError as e:
            error_message = f"Xin lỗi, có lỗi xảy ra khi parse JSON: {e}"
            return error_message, "json_error"
            
    except Exception as e:
        error_message = f"Xin lỗi, có lỗi xảy ra: {e}"
        return error_message, "system_error"
    

def route_to_stage(stage_manager, response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Điều hướng request đến stage tương ứng
    
    Args:
        stage_manager: Đối tượng quản lý stage
        response_text: Phản hồi từ AI
        summary: Tóm tắt ý định
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
    
    Returns:
        tuple: (final_response, final_summary)
    """
    
    # Case 1: Đang ở main stage - Phân tích ý định ban đầu
    if stage_manager.is_in_main_stage():
        if summary == 'tạo ticket':
            stage_manager.switch_stage('create')
            return create.handle_create_stage(response_text, summary, user_input, chain, chat_history)
            
        elif summary == 'sửa ticket':
            stage_manager.switch_stage('edit')
            return edit.handle_edit_stage(response_text, summary, user_input, chain, chat_history)
            
        elif summary == 'thoát':
            return response_text, summary
            
        else:  # không xác định
            return response_text, summary
    
    # Case 2: Đang ở create stage - Tiếp tục xử lý tạo ticket
    elif stage_manager.current_stage == 'create':
        final_response, final_summary = create.handle_create_stage(
            response_text, summary, user_input, chain, chat_history
        )
        
        # Chuyển về main stage nếu hoàn thành hoặc thoát
        if final_summary in ['ticket_created', 'sửa ticket', 'thoát', 'main']:
            stage_manager.switch_stage('main')
            
        return final_response, final_summary
    
    # Case 3: Đang ở edit stage - Tiếp tục xử lý sửa ticket
    elif stage_manager.current_stage == 'edit':
        final_response, final_summary = edit.handle_edit_stage(
            response_text, summary, user_input, chain, chat_history
        )
        
        # Chuyển về main stage nếu hoàn thành hoặc thoát
        if final_summary in ['ticket_edited', 'tạo ticket', 'thoát', 'main']:
            stage_manager.switch_stage('main')
            
        return final_response, final_summary
    
    # Fallback: Trả về response gốc
    return response_text, summary



# Utility function để convert sang JSON nếu cần
def dict_to_json(parsed_dict, pretty=True):
    """
    Convert parsed dictionary sang JSON string
    
    Args:
        parsed_dict (dict): Dictionary đã parse
        pretty (bool): Format JSON với indentation
    
    Returns:
        str: JSON string
    """
    try:
        indent = 4 if pretty else None
        return json.dumps(parsed_dict, indent=indent, ensure_ascii=False)
    except Exception as e:
        error_dict = {'error': f'JSON conversion failed: {str(e)}'}
        return json.dumps(error_dict, ensure_ascii=False)



def exit_chat(chat_history):
    """
    Kết thúc cuộc hội thoại và ghi dấu kết thúc vào file
    """
    file_path = f"{config.DATA_PATH}/{chat_history.session_filename}"
    with open(file_path, "a", encoding='utf-8') as f:
        f.write(f"\n=== Cuộc trò chuyện đã kết thúc tại {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")