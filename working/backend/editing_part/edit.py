from backend.starting_part.start import *

"""
Module xử lý logic sửa ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
"""

import backend.utils as utils
import configuration.config as config
import json

def edit_ticket(chain, chat_history, user_input, context, response_text, summary, ticket_data):
    """
    Xử lý logic sửa ticket dựa trên input đã nhận từ start.py
    
    Args:
        chain: Chuỗi xử lý LangChain đã được khởi tạo
        chat_history: Đối tượng ChatHistory để duy trì lịch sử hội thoại
        user_input: Input của người dùng đã được lấy từ start.py
        context: Ngữ cảnh cho AI
    
    Returns:
        tuple: (response_text, summary, ticket_data) - Phản hồi cho người dùng và ý định tiếp theo
    """
    
    # Gọi AI để xử lý input trong ngữ cảnh sửa ticket
    try:
        # Kiểm tra nếu response_text là JSON string, parse nó
        if isinstance(response_text, str) and response_text.strip().startswith('{'):
            try:
                parsed_response = json.loads(response_text)
                response_text = parsed_response.get("response", response_text)
                summary = parsed_response.get("summary", summary)
                ticket_data = parsed_response.get("ticket_data", ticket_data)
                print(f"Debug - Parsed response_text: {response_text}")
                print(f"Debug - Parsed summary: {summary}")
                print(f"Debug - Parsed ticket_data: {ticket_data}")
            except json.JSONDecodeError:
                # Nếu không parse được JSON, giữ nguyên response_text
                pass
        
        # Thêm logic xử lý đặc biệt cho sửa ticket ở đây nếu cần
        # Ví dụ: tìm ticket cần sửa, validate dữ liệu mới, etc.
        
        if not summary:  # Nếu như hàm get_response bị lỗi parse, trả lại summary là sửa ticket và response gốc
            summary = "sửa ticket"
        print(f"Debug - Final Summary: {summary}")
        
        return response_text, summary, ticket_data
        
    except Exception as e:
        print(f"Error in edit_ticket: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket. Lỗi: {e}"
        return error_response, "sửa ticket", None  # Giữ nguyên trạng thái sửa ticket
        