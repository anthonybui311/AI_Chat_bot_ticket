# create.py
"""
Module xử lý logic tạo ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
"""

import backend.starting_part.start as start

def create_ticket(chain, chat_history, user_input, context):
    """
    Xử lý logic tạo ticket dựa trên input đã nhận từ start.py
    
    Args:
        chain: Chuỗi xử lý LangChain đã được khởi tạo
        chat_history: Đối tượng ChatHistory để duy trì lịch sử hội thoại
        user_input: Input của người dùng đã được lấy từ start.py
        context: Ngữ cảnh cho AI
    
    Returns:
        tuple: (response_text, summary) - Phản hồi cho người dùng và ý định tiếp theo
    """
    
    # Gọi AI để xử lý input trong ngữ cảnh tạo ticket
    try:
        response_text, summary = start.get_response(chain, chat_history, user_input, context)
        
        # Thêm logic xử lý đặc biệt cho tạo ticket ở đây nếu cần
        # Ví dụ: lưu thông tin ticket vào database, validate dữ liệu, etc.
        if not summary: # Nếu như hàm get_response bị lỗi parse, trả lại summary là tạo ticket và response gốc
            summary = "tạo ticket"
        return response_text, summary
        
    except Exception as e:
        print(f"Error: {e}")
        error_response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu tạo ticket. Vui lòng thử lại."
        return error_response, "tạo ticket"  # Giữ nguyên trạng thái tạo ticket


def validate_ticket_data(ticket_data):
    """
    Validate dữ liệu ticket trước khi lưu (tùy chọn)
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
    
    Returns:
        bool: True nếu dữ liệu hợp lệ, False nếu không
    """
    required_fields = ['title', 'description', 'priority', 'type']
    
    for field in required_fields:
        if field not in ticket_data or not ticket_data[field].strip():
            return False
    
    return True

def save_ticket_to_database(ticket_data):
    """
    Lưu ticket vào database (ví dụ - chưa implement)
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
    
    Returns:
        str: ID của ticket đã tạo hoặc None nếu lỗi
    """
    # TODO: Implement database saving logic
    # Ví dụ: kết nối database, insert ticket, trả về ID
    pass
