from dotenv import load_dotenv # type: ignore
load_dotenv()


from datetime import datetime
from langchain_groq import ChatGroq # type: ignore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # type: ignore
from langchain_core.messages import HumanMessage, AIMessage # type: ignore
import json
import configuration.config as config
import backend.creating_part.create as create
import backend.editing_part.edit as edit
import backend.api_call as api



# --- STAGE MANAGER CLASS ---
class StageManager:
    """
    EXPANDED CLASS: Quản lý trạng thái stage của hệ thống
    - Theo dõi stage hiện tại
    - Chuyển đổi context tương ứng
    - Duy trì trạng thái xuyên suốt session
    - NEW: Hỗ trợ CONFIRMATION và CORRECT stages
    """
    
    def __init__(self):
        # EXPANDED: Thêm 2 stage mới
        self.current_stage = "main"  # Các stage: main, create, edit, confirmation, correct
        self.stage_contexts = {
            "main": config.CONTEXT,
            "create": config.CREATE_CONTEXT,
            "edit": config.EDIT_CONTEXT,
            "confirmation": config.CONFIRMATION_CONTEXT,  # NEW
            "correct": config.CORRECT_CONTEXT              # NEW
        }
        
        # NEW: Lưu trữ thông tin ticket để chuyển giữa các stage
        self.pending_ticket_data = None
    
    def get_current_context(self):
        """Lấy context cho stage hiện tại"""
        return self.stage_contexts.get(self.current_stage, config.CONTEXT)
    
    def switch_stage(self, new_stage):
        """IMPROVED: Chuyển đổi sang stage mới với validation"""
        if new_stage in self.stage_contexts:
            old_stage = self.current_stage
            self.current_stage = new_stage
            print(f"[STAGE] {old_stage} → {new_stage}")
            return True
        else:
            print(f"[ERROR] Invalid stage: {new_stage}")
            return False
    
    def is_in_main_stage(self):
        """Kiểm tra có đang ở main stage không"""
        return self.current_stage == "main"
    
    # NEW: Methods for new stages
    def is_in_confirmation_stage(self):
        """Kiểm tra có đang ở confirmation stage không"""
        return self.current_stage == "confirmation"
    
    def is_in_correct_stage(self):
        """Kiểm tra có đang ở correct stage không"""
        return self.current_stage == "correct"
    
    def store_ticket_data(self, ticket_data):
        """NEW: Lưu trữ thông tin ticket để sử dụng ở các stage khác"""
        self.pending_ticket_data = ticket_data
        print(f"[TICKET] Stored: {ticket_data}")
    
    def get_stored_ticket_data(self):
        """NEW: Lấy thông tin ticket đã lưu"""
        return self.pending_ticket_data
    
    def clear_ticket_data(self):
        """NEW: Xóa thông tin ticket đã lưu"""
        self.pending_ticket_data = None
        print("[TICKET] Cleared stored data")

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
        print(f"[SESSION] Started: {self.session_filename}")
    
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
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
        model_kwargs={
        "service_tier": "auto"  # or "on_demand" or "auto"
        }
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
            print(f"JSON: {result}")
            
            # Extract response và summary
            response_field = result.get("response", "")
            summary = result.get("summary", None)
            
            print(f"[AI] Response type: {type(response_field)}, Summary: {summary}")
            return response_field, summary
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}")
            error_message = f"Xin lỗi, có lỗi xảy ra khi parse JSON: {e}"
            return error_message, "json_error"
            
    except Exception as e:
        print(f"[ERROR] Chain invoke failed: {e}")
        error_message = f"Xin lỗi, có lỗi xảy ra: {e}"
        return error_message, "thoát"

def route_to_stage(stage_manager, response_text, summary, user_input, chain, chat_history):
    """
    EXPANDED FUNCTION: Điều hướng request đến stage tương ứng
    NEW: Hỗ trợ CONFIRMATION và CORRECT stages
    
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
    
    print(f"[ROUTE] Stage: {stage_manager.current_stage}, Summary: {summary}")
    
    # Case 1: Đang ở main stage - Phân tích ý định ban đầu
    if stage_manager.is_in_main_stage():
        if summary == 'tạo ticket' : #or isinstance(response_text, dict)
            stage_manager.switch_stage('create')
            return create.handle_create_stage(response_text, summary, user_input, chain, chat_history, stage_manager)
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
            response_text, summary, user_input, chain, chat_history, stage_manager
        )

        # NEW: Chỉ chuyển sang CONFIRMATION stage nếu user xác nhận đúng VÀ có ticket data
        if final_summary == "đúng":
            # Kiểm tra lại ticket data trước khi chuyển stage
            stored_ticket_data = stage_manager.get_stored_ticket_data()
            if stored_ticket_data:
                stage_manager.switch_stage('confirmation')
                return handle_confirmation_stage(stage_manager, final_response, final_summary, user_input, chain, chat_history)
            else:
                # Không có ticket data, ở lại create stage
                return final_response, "tạo ticket"
        
        # Chuyển sang CONFIRMATION stage nếu có ticket data đầy đủ
        elif final_summary == "chờ xác nhận":
            stage_manager.switch_stage('confirmation')
            return final_response, final_summary

        # Chuyển về main stage nếu user muốn sửa hoặc thoát
        elif final_summary == 'thoát':
            stage_manager.switch_stage('main')
            stage_manager.clear_ticket_data()
            return final_response, final_summary
        
        elif final_summary == 'sửa ticket':
            stage_manager.switch_stage('edit')
            stage_manager.clear_ticket_data()
            return final_response, final_summary
        # Tiếp tục ở create stage

        return final_response, final_summary

    
    # Case 3: Đang ở edit stage - Tiếp tục xử lý sửa ticket
    elif stage_manager.current_stage == 'edit':
        final_response, final_summary = edit.handle_edit_stage(response_text, summary, user_input, chain, chat_history)
        
        # Chuyển về main stage nếu users muốn tạo hoặc thoát
        if final_summary == 'thoát':
            stage_manager.switch_stage('main')
            return final_response, final_summary
        elif final_summary == 'tạo ticket':
            stage_manager.switch_stage('create')
            return final_response, final_summary
            
            
        return final_response, final_summary
    
    # NEW Case 4: Đang ở confirmation stage - Xử lý xác nhận
    elif stage_manager.is_in_confirmation_stage():
        return handle_confirmation_stage(stage_manager, response_text, summary, user_input, chain, chat_history)
    
    # NEW Case 5: Đang ở correct stage - Xử lý ticket
    elif stage_manager.is_in_correct_stage():
        return handle_correct_stage(stage_manager, response_text, summary, user_input, chain, chat_history)
    
    
    #TODO: New Case 6: Đang ở main stage - Ticket được tạo, tạm thời về lại main
    
    
    # Fallback: Trả về response gốc
    return response_text, summary

def handle_confirmation_stage(stage_manager, response_text, summary, user_input, chain, chat_history):
    """
    IMPROVED FUNCTION: Xử lý logic cho CONFIRMATION stage
    FIXED: Lưu ticket_data trước khi AI thay đổi response_text
    
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
    
    try:
        print(f"[CONFIRMATION] Processing summary: {summary}")
        
        # Case 1: User xác nhận ĐÚNG - Chuyển sang CORRECT stage
        if summary == 'đúng':
            stage_manager.switch_stage('correct')
            return handle_correct_stage(stage_manager, response_text, 'đang xử lý', user_input, chain, chat_history)
        
        # Case 2: User xác nhận SAI - Quay về CREATE stage
        elif summary == 'sai':
            stage_manager.switch_stage('create')
            stage_manager.clear_ticket_data()  # Xóa dữ liệu ticket cũ
            return response_text, "tạo ticket"
        
        # Case 3: Chuyển sang edit stage
        elif summary == 'sửa ticket':
            stage_manager.switch_stage('edit')
            stage_manager.clear_ticket_data()  # Xóa dữ liệu ticket cũ
            return response_text, summary
        
        # Case 4: Thoát khỏi hệ thống
        elif summary == 'thoát':
            stage_manager.switch_stage('main')
            stage_manager.clear_ticket_data()  # Xóa dữ liệu ticket cũ
            return response_text, summary
        
        # Case 5: Không xác định - Ở lại confirmation stage
        else:
            return response_text, "chờ xác nhận"
            
    except Exception as e:
        print(f"[ERROR] Confirmation stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra trong quá trình xác nhận: {e}"
        return error_response, "thoát"


def handle_correct_stage(stage_manager, response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý logic cho CORRECT stage
    
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
    
    try:
        print(f"[CORRECT] Processing summary: {summary}")
        
        # Case 1: Đang xử lý ticket
        if summary == 'đang xử lý':
            # Lấy ticket data đã lưu
            ticket_data = stage_manager.get_stored_ticket_data()
            
            if ticket_data:
                # Tạo ticket ID và lưu vào database
                ci_data = create.check_ticket_on_database(ticket_data)
                if not ci_data: # then create ticket
                    return handle_creating_ticket(ticket_data)
                
                #TODO: Implement logic to handle 1 CI data
                elif len(ci_data) == 1:
                    pass
                elif len(ci_data) > 1:
                    response_text = "Mình kiểm tra trên hệ thống thấy có nhiều dữ liệu về thiết bị mà bạn đã cung cấp: {ci_data}. Bạn vui lòng kiểm tra và cung cấp giúp mình thông tin S/N cần mở ticket."
                    #TODO new stage for user to choose ci_data
                return "checking", "ticket đã được tạo"
            else:
                return cannot_create_ticket()
        
        # Case 2: Hoàn thành xử lý
        elif summary == 'hoàn thành':
            stage_manager.switch_stage('main')
            stage_manager.clear_ticket_data()
            return response_text, "ticket đã được tạo"
        
        # Case 3: Thoát khỏi hệ thống
        elif summary == 'thoát':
            stage_manager.switch_stage('main')
            stage_manager.clear_ticket_data()
            return response_text, summary
        
        # Case 4: Fallback - Tiếp tục ở correct stage
        else:
            return response_text, summary
            
    except Exception as e:
        print(f"[ERROR] Correct stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra trong quá trình xử lý ticket: {e}"
        return error_response, "thoát"

def handle_1_ci_data(ci_data):
    """
    Xử lý trường hợp có 1 CI data
    """
    print(f"[CI DATA] Found 1 CI: {ci_data}")
    
    ci = ci_data[0]
    serial_number = ci.get('serial_number', 'Không có S/N')
    ticket = api.get_all_ticket_for_sn(serial_number)
    




def handle_creating_ticket(ticket_data):
    try:
        ticket_id = api.post_create_ticket("bkk", ticket_data['serial_number'], "open-inprogress", "all")
        if not ticket_id:
            return cannot_create_ticket()
        
        # tạo thành công ticket và thoát
        response_text = f"Mình đã tạo ticket thành công trên hệ thống. Thông tin phiếu: {ticket_id}. Cảm ơn bạn đã liên hệ, chào tạm biệt bạn! "
        return response_text, "thoát"
    except Exception as e:
        response_text = (f"[ERROR] Create ticket: {e}")
        # Xử lý lỗi không thể tạo ticket
        return response_text, "thoát"

def cannot_create_ticket():
    """
    Xử lý trường hợp không thể tạo ticket
    """
    print("[CREATE] Ticket creation failed.")
    response_text = "Rất xin lỗi bạn, do hệ thống đang gặp sự cố, mình chưa thể tạo ticket cho bạn được. Bạn vui lòng thực hiện lại sau. Cảm ơn bạn, chào tạm biệt bạn"
    return response_text, "thoát"

def cancel_create_ticket():
    """
    Hủy bỏ quá trình tạo ticket
    """
    print("[CREATE] Ticket creation cancelled.")
    response_text = "Mình đã thực hiện hủy yêu cầu tạo phiếu của bạn rồi ạ. Cảm ơn bạn đã liên hệ, chào tạm biệt bạn!"
    return response_text, "thoát"


def exit_chat(chat_history):
    """
    Kết thúc cuộc hội thoại và ghi dấu kết thúc vào file
    """
    file_path = f"{config.DATA_PATH}/{chat_history.session_filename}"
    with open(file_path, "a", encoding='utf-8') as f:
        f.write(f"\n=== Cuộc trò chuyện đã kết thúc tại {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    print(f"[SESSION] Ended: {chat_history.session_filename}")
