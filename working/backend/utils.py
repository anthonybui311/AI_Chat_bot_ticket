from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import json
import configuration.config as config

# --- CHAT HISTORY CLASS (giữ nguyên) ---
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
    Lấy phản hồi từ AI chatbot
    
    Args:
        chain: Chuỗi xử lý LangChain
        chat_history: Đối tượng ChatHistory
        question: Câu hỏi của người dùng
        context: Ngữ cảnh bổ sung (tùy chọn)
    
    Returns:
        tuple: (response_text, summary, ticket_data) - Câu trả lời và ý định
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
            
            # Extract các trường riêng biệt từ JSON response
            response_text = result.get("response", "")
            summary = result.get("summary", None)
            ticket_data = result.get("ticket_data", None)
            
            print(f"Debug - Extracted response_text: {response_text}")
            print(f"Debug - Extracted summary: {summary}")
            print(f"Debug - Extracted ticket_data: {ticket_data}")
            
            return response_text, summary, ticket_data
            
        except json.JSONDecodeError as e:
            
            # Nếu lỗi parse JSON, cố gắng extract thông tin từ text thô
            response_text = content
            summary = None
            ticket_data = None
            
            # Cố gắng tìm summary từ text (fallback)
            if any(keyword in content.lower() for keyword in ['tạo ticket', 'create ticket']):
                summary = 'tạo ticket'
            elif any(keyword in content.lower() for keyword in ['sửa ticket', 'edit ticket']):
                summary = 'sửa ticket'
            elif any(keyword in content.lower() for keyword in ['tạm biệt', 'bye', 'thoát']):
                summary = 'tạm biệt'
                
            return response_text, summary, ticket_data
        
    except Exception as e:
        error_message = f"Xin lỗi, có lỗi xảy ra: {e}"
        return error_message, None, None


def exit_chat(chat_history):
    """
    Kết thúc cuộc hội thoại và ghi dấu kết thúc vào file
    """
    file_path = f"{config.DATA_PATH}/{chat_history.session_filename}"
    with open(file_path, "a", encoding='utf-8') as f:
        f.write(f"\n=== Cuộc trò chuyện đã kết thúc tại {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    print("Chatbot: Tạm Biệt! Cảm ơn bạn đã sử dụng dịch vụ của mình")
    print(f"Cuộc trò chuyện đã được lưu vào file: {chat_history.session_filename}")