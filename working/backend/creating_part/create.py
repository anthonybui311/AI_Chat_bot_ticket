# create.py

"""
Module xử lý logic tạo ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
IMPROVED: Sử dụng response_data làm ticket_data trực tiếp
"""

import backend.utils as utils
import configuration.config as config
import backend.utils as utils
import json
from datetime import datetime

def handle_create_stage(response_text, summary, user_input, chain, chat_history, stage_manager):
    """
    IMPROVED FUNCTION: Xử lý toàn bộ logic cho create stage
    
    Args:
        response_text: Phản hồi từ AI
        summary: Tóm tắt ý định
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (final_response, final_summary)
    """
    
    try:
        print(f"[CREATE] Response type: {type(response_text)}")
        
        # Case 1: Chuyển sang edit stage
        if summary == 'sửa ticket':
            return response_text, summary
            
        # Case 2: Thoát khỏi hệ thống
        elif summary == 'thoát':
            return response_text, summary
            
        # Case 3: Response là dictionary (thông tin ticket)
        elif isinstance(response_text, dict):
            return process_ticket_data(response_text, user_input, chain, chat_history, stage_manager)
            
        # Case 4: Response là string (phản hồi thông thường hoặc hướng dẫn)
        elif isinstance(response_text, str):
            return process_string_response(response_text, summary, user_input, chain, chat_history)
            
        # Case 5: Fallback
        else:
            error_response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại."
            return error_response, "tạo ticket"
            
    except Exception as e:
        print(f"[ERROR] Create stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu tạo ticket: {e}"
        return error_response, "system_error"

def process_ticket_data(ticket_data, user_input, chain, chat_history, stage_manager):
    """
    IMPROVED FUNCTION: Xử lý khi response là dictionary chứa thông tin ticket
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    print(f"[CREATE] Processing ticket: {list(ticket_data.keys())}")
    
    # Validate ticket data
    is_complete, missing_fields = validate_ticket_data(ticket_data)
    
    if is_complete:
        # Ticket đầy đủ thông tin - Hiển thị để xác nhận
        confirmation_response = format_ticket_confirmation(ticket_data)
        stage_manager.store_ticket_data(ticket_data)
        print(f"[CREATE] Confirmation response: {confirmation_response}")
        
        return confirmation_response, "chờ xác nhận"
    else:
        # Ticket thiếu thông tin - Yêu cầu bổ sung
        missing_fields_str = ", ".join([field_translation.get(f, f) for f in missing_fields])
        request_response = f"Thông tin ticket còn thiếu: {missing_fields_str}. Vui lòng cung cấp thêm thông tin."
        return request_response, "tạo ticket"

def process_string_response(response_text, summary, user_input, chain, chat_history):
    """
    SIMPLIFIED FUNCTION: Xử lý khi response là string
    IMPROVED: Không cần xử lý confirmation ở đây vì CONFIRMATION stage sẽ handle
    
    Args:
        response_text: String response từ AI
        summary: Tóm tắt ý định
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    # SIMPLIFIED: Chỉ trả về response gốc với summary tương ứng
    # CONFIRMATION stage sẽ xử lý logic xác nhận
    return response_text, summary if summary else "tạo ticket"

def validate_ticket_data(ticket_data):
    """
    IMPROVED: Validate dữ liệu ticket trước khi lưu
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
        
    Returns:
        tuple: (bool, list)
        - bool: True nếu dữ liệu hợp lệ, False nếu có lỗi
        - list: Danh sách các trường còn thiếu
    """
    
    required_fields = ['serial_number', 'device_type', 'problem_description']
    missing_fields = []
    
    if not isinstance(ticket_data, dict):
        return False, required_fields
    
    for field in required_fields:
        value = ticket_data.get(field, '')
        if not value or not str(value).strip():
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

def format_ticket_confirmation(ticket_data):
    """
    IMPROVED FUNCTION: Format thông tin ticket để xác nhận
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
        
    Returns:
        str: Chuỗi thông tin ticket được format
    """
    
    serial_number = ticket_data.get('serial_number', 'Chưa có')
    device_type = ticket_data.get('device_type', 'Chưa có')
    problem_description = ticket_data.get('problem_description', 'Chưa có')
    
    confirmation_text = f"""Mình xin xác nhận thông tin như sau:

• S/N hoặc ID thiết bị: {serial_number}
• Loại thiết bị: {device_type}
• Nội dung sự cố: {problem_description}

Thông tin này có chính xác không ạ?"""
    
    return confirmation_text

def save_ticket_to_database(ticket_data):
    """
    IMPROVED: Lưu ticket vào database (placeholder implementation)
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
        
    Returns:
        str: ID của ticket đã tạo
    """
    
    try:
        # TODO: Implement actual database saving logic
        # For now, generate a mock ticket ID
        ticket_id = f"TK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Log ticket information (for debugging)
        print(f"[TICKET] Saved ID: {ticket_id}")
        print(f"[TICKET] Data: {ticket_data}")
        
        return ticket_id
        
    except Exception as e:
        print(f"[ERROR] Save ticket: {e}")
        return f"ERROR_{datetime.now().strftime('%H%M%S')}"

# Translation mapping for user-friendly field names
field_translation = {
    'serial_number': 'S/N hoặc ID thiết bị',
    'device_type': 'Loại thiết bị',
    'problem_description': 'Nội dung sự cố'
}
