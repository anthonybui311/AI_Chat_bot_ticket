# start.py

"""
File chính chịu trách nhiệm:
- Lấy input từ người dùng (duy nhất ở đây)
- Phân tích ý định người dùng NGAY LẬP TỨC
- Điều hướng đến các module xử lý tương ứng
- Duy trì lịch sử hội thoại liên tục
"""

import backend.editing_part.edit as edit
import backend.creating_part.create as create
import json
import configuration.config as config
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

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
        tuple: (response_text, summary) - Câu trả lời và ý định
    """
    chain_input = {
        "question": question,
        "context": context,
        "chat_history": chat_history.get_messages()
    }
    response = chain.invoke(chain_input)
    
    # Parse JSON output
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        result = json.loads(content)
        return result["response"], result["summary"]
    except Exception as e:
        # Nếu lỗi parse, trả về response gốc và None
        return content, None

def exit_chat(chat_history):
    """
    Kết thúc cuộc hội thoại và ghi dấu kết thúc vào file
    """
    file_path = f"{config.DATA_PATH}/{chat_history.session_filename}"
    with open(file_path, "a", encoding='utf-8') as f:
        f.write(f"\n=== Cuộc trò chuyện đã kết thúc tại {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    print("Chatbot: Tạm Biệt! Cảm ơn bạn đã sử dụng dịch vụ của mình")
    print(f"Cuộc trò chuyện đã được lưu vào file: {chat_history.session_filename}")

# --- MAIN FUNCTION ---
def start():
    """
    Hàm chính điều khiển toàn bộ luồng chatbot:
    - Khởi tạo chain và chat history
    - Chạy vòng lặp chính để lấy input từ người dùng
    - Phân tích ý định NGAY LẬP TỨC và điều hướng đến module tương ứng
    - Duy trì lịch sử hội thoại liên tục
    """
    print("Chatbot được khởi động. Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện.")
    
    # Khởi tạo chain và chat history - TẠO SESSION MỚI
    chain = create_chain()
    chat_history = ChatHistory()
    
    # Context cho AI để hiểu nhiệm vụ 
    context = """Bạn là một AI chatbot hỗ trợ quản lý ticket.
        Nhiệm vụ của bạn:
        Khi bắt đầu hội thoại, hãy sử dụng chính xác câu chào sau dưới dạng text thuần túy:
        "Chào bạn! Mình là trợ lý hỗ trợ về ticket. Bạn muốn tạo ticket hay sửa nội dung ticket đã có?"

        Khi người dùng gửi tin nhắn, hãy phân tích và xác định ý định chính của họ là một trong các trường hợp sau:
        "tạo ticket"
        "sửa ticket"
        "thoát" hoặc "tạm biệt" (nếu người dùng muốn kết thúc hoặc rời khỏi hội thoại)
        Nếu không xác định được ý định, hãy trả về response phù hợp và đặt summary là "không xác định"

        Trả về kết quả dưới dạng JSON với 2 trường:
        "response": câu trả lời gửi cho người dùng (text thuần túy, không giải thích thêm).
        "summary": ý định chính, chỉ nhận một trong các giá trị: "tạo ticket", "sửa ticket", "thoát", "tạm biệt", "không xác định".

        Ví dụ:
        Người dùng: "Tôi muốn tạo ticket mới."
        {"response": "Tôi sẽ giúp bạn tạo ticket mới.", "summary": "tạo ticket"}

        Người dùng: "Tôi cần chỉnh sửa ticket cũ."
        {"response": "Bạn muốn sửa nội dung ticket nào? Vui lòng cung cấp thêm thông tin.", "summary": "sửa ticket"}

        Người dùng: "Cảm ơn, tôi không cần hỗ trợ nữa."
        {"response": "Cảm ơn bạn đã sử dụng dịch vụ. Hẹn gặp lại!", "summary": "tạm biệt"}

        Người dùng: "Thoát"
        {"response": "Bạn đã thoát khỏi phiên hỗ trợ. Nếu cần trợ giúp, hãy quay lại bất cứ lúc nào.", "summary": "thoát"}

        Người dùng: "Hôm nay trời đẹp quá!"
        {"response": "Xin lỗi, mình chưa hiểu ý bạn. Bạn muốn tạo ticket hay sửa ticket?", "summary": "không xác định"}

        Chỉ trả về đúng định dạng JSON trên, không thêm bất kỳ thông tin nào khác."""

    while True:
        # Lấy input từ người dùng (chỉ ở đây, không ở file khác)
        user_input = input("\nBạn: ")

        # Kiểm tra điều kiện thoát trước khi xử lý
        if user_input.lower() in ['tạm biệt', 'thoát', 'bye', 'exit', 'quit']:
            exit_chat(chat_history)
            break

        # PHÂN TÍCH Ý ĐỊNH NGAY LẬP TỨC sau khi nhận input
        try:
            response_text, summary = get_response(
                chain=chain,
                chat_history=chat_history,
                question=user_input,
                context=context
            )
            
            # ĐIỀU HƯỚNG NGAY LẬP TỨC dựa trên summary vừa phân tích
            if summary == 'tạo ticket':
                # Tạo context chuyên biệt cho việc tạo ticket
                create_context = context + """

                    Hiện tại bạn đang ở chế độ TẠO TICKET.
                    Hãy hướng dẫn người dùng cung cấp thông tin cần thiết để tạo ticket mới:
                    - Tiêu đề ticket
                    - Mô tả chi tiết vấn đề
                    - Mức độ ưu tiên (thấp/trung bình/cao/khẩn cấp)
                    - Loại ticket (bug/feature/support)

                    Yêu cầu người dùng nhập toàn bộ thông tin trong dòng

                    Nếu người dùng muốn chuyển sang sửa ticket hoặc thoát, hãy cập nhật summary tương ứng.
                    Nếu người dùng lại ấn thêm chế độ tạo ticket, thì không thay đổi summary.
                    """
                
                # Gọi hàm create ticket với input hiện tại
                response_text, summary = create.create_ticket(chain, chat_history, user_input, create_context)
                
            elif summary == 'sửa ticket':
                # Gọi hàm edit ticket với input hiện tại
                response_text, summary = edit.edit_ticket(chain, chat_history, user_input, context)
                
            elif summary in ['tạm biệt', 'thoát']:
                # Lưu tin nhắn trước khi thoát
                chat_history.add_user_message(user_input)
                chat_history.add_ai_message(response_text)
                print(f"Chatbot: {response_text}")
                exit_chat(chat_history)
                break
            
            # Lưu tin nhắn vào lịch sử (cho tất cả trường hợp)
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(response_text)
            print(f"Chatbot: {response_text}")
                
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    start()
