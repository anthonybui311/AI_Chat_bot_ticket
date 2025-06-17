# create.py

"""
Module xử lý logic tạo ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
IMPROVED: Hoàn thiện logic xử lý multi-stage
"""

import backend.utils as utils
import configuration.config as config
import json
from datetime import datetime

def handle_create_stage(response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý toàn bộ logic cho create stage
    
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
        print(f"[CREATE DEBUG] Processing - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: Chuyển sang edit stage
        if summary == 'sửa ticket':
            return response_text, summary
            
        # Case 2: Thoát khỏi hệ thống
        elif summary == 'thoát':
            return response_text, summary
            
        # Case 3: Response là dictionary (thông tin ticket)
        elif isinstance(response_text, dict):
            return process_ticket_data(response_text, user_input, chain, chat_history)
            
        # Case 4: Response là string (phản hồi thông thường hoặc hướng dẫn)
        elif isinstance(response_text, str):
            return process_string_response(response_text, summary, user_input, chain, chat_history)
            
        # Case 5: Fallback
        else:
            error_response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại."
            return error_response, "tạo ticket"
            
    except Exception as e:
        print(f"[CREATE ERROR] {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu tạo ticket: {e}"
        return error_response, "system_error"

def process_ticket_data(ticket_data, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý khi response là dictionary chứa thông tin ticket
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    print(f"[CREATE DEBUG] Processing ticket data: {ticket_data}")
    
    # Validate ticket data
    is_complete, missing_fields = validate_ticket_data(ticket_data)
    
    if is_complete:
        # Ticket đầy đủ thông tin - Hiển thị để xác nhận
        confirmation_response = format_ticket_confirmation(ticket_data)
        return confirmation_response, "awaiting_confirmation_create"
    else:
        # Ticket thiếu thông tin - Yêu cầu bổ sung
        missing_fields_str = ", ".join([field_translation.get(f, f) for f in missing_fields])
        request_response = f"Thông tin ticket còn thiếu: {missing_fields_str}. Vui lòng cung cấp thêm thông tin."
        return request_response, "tạo ticket"

def process_string_response(response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý khi response là string
    
    Args:
        response_text: String response từ AI
        summary: Tóm tắt ý định
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    # FIXED: Kiểm tra xem có phải là phản hồi xác nhận không
    if is_confirmation_response(user_input):
        print(f"[CREATE DEBUG] Detected confirmation response: {user_input}")
        return handle_ticket_confirmation(user_input, chain, chat_history)
    
    # Trả về response gốc với summary tương ứng
    return response_text, summary if summary else "tạo ticket"

def handle_ticket_confirmation(user_input, chain, chat_history):
    """
    FIXED FUNCTION: Xử lý phản hồi xác nhận ticket từ người dùng
    
    Args:
        user_input: Input xác nhận từ người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    # FIXED: Phân tích input xác nhận với các từ khóa chính xác
    confirmation_keywords_positive = ['đúng', 'chính xác', 'ok', 'yes', 'correct', 'phải', 'vâng', 'ừ', 'uh huh', 'đồng ý']
    confirmation_keywords_negative = ['sai', 'không chính xác', 'không ok', 'no', 'incorrect', 'không phải', 'không đúng', 'không đồng ý']
    
    user_input_lower = user_input.lower().strip()
    print(f"[CREATE DEBUG] Analyzing confirmation input: '{user_input_lower}'")
    
    # FIXED: Xác nhận ĐÚNG - Tạo ticket
    is_positive = any(keyword in user_input_lower for keyword in confirmation_keywords_positive)
    is_negative = any(keyword in user_input_lower for keyword in confirmation_keywords_negative)
    
    print(f"[CREATE DEBUG] Is positive: {is_positive}, Is negative: {is_negative}")
    
    if is_positive and not is_negative:
        # Lấy thông tin ticket từ lịch sử chat gần đây nhất
        ticket_info = extract_ticket_from_history(chat_history)
        
        if ticket_info:
            # Lưu ticket
            ticket_id = save_ticket_to_database(ticket_info)
            success_response = f"Ticket đã được tạo thành công với ID: {ticket_id}. Cảm ơn bạn đã sử dụng dịch vụ!"
            return success_response, "ticket_created"  # FIXED: Changed from "ticket được tạo" to "ticket_created"
        else:
            error_response = "Không thể tìm thấy thông tin ticket để lưu. Vui lòng thử lại."
            return error_response, "tạo ticket"
    
    # FIXED: Xác nhận SAI - Yêu cầu nhập lại
    elif is_negative and not is_positive:
        retry_response = "Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin chính xác để mình tạo ticket mới cho bạn."
        return retry_response, "tạo ticket"
    
    # FIXED: Không rõ ràng - Hỏi lại
    else:
        clarify_response = "Mình chưa hiểu ý bạn. Thông tin ticket trên có chính xác không? Vui lòng trả lời 'đúng' hoặc 'sai'."
        return clarify_response, "awaiting_confirmation_create"

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
    NEW FUNCTION: Format thông tin ticket để xác nhận
    
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

def is_confirmation_response(user_input):
    """
    FIXED FUNCTION: Kiểm tra xem input có phải là phản hồi xác nhận không
    
    Args:
        user_input: Input của người dùng
        
    Returns:
        bool: True nếu là phản hồi xác nhận
    """
    
    confirmation_indicators = [
        'đúng', 'sai', 'chính xác', 'không chính xác', 'ok', 'không ok',
        'yes', 'no', 'correct', 'incorrect', 'phải', 'không phải',
        'vâng', 'không', 'ừ', 'uh huh', 'đồng ý', 'không đồng ý'
    ]
    
    user_input_lower = user_input.lower().strip()
    
    # FIXED: Kiểm tra input có chứa từ khóa xác nhận
    # Không giới hạn số từ vì người dùng có thể nói "đúng rồi", "sai rồi", etc.
    return any(indicator in user_input_lower for indicator in confirmation_indicators)

def extract_ticket_from_history(chat_history):
    """
    FIXED FUNCTION: Trích xuất thông tin ticket từ lịch sử chat
    
    Args:
        chat_history: Đối tượng ChatHistory
        
    Returns:
        dict: Thông tin ticket hoặc None nếu không tìm thấy
    """
    
    # Tìm trong các tin nhắn AI gần đây nhất để tìm thông tin ticket
    messages = chat_history.get_messages()
    
    # Duyệt ngược từ tin nhắn gần nhất
    for message in reversed(messages):
        if hasattr(message, 'content') and 'S/N hoặc ID thiết bị:' in message.content:
            # Parse thông tin ticket từ message content
            try:
                lines = message.content.split('\n')
                ticket_info = {}
                
                for line in lines:
                    line = line.strip()
                    if 'S/N hoặc ID thiết bị:' in line:
                        value = line.split(':', 1)[1].strip()
                        if value and value != 'Chưa có':
                            ticket_info['serial_number'] = value
                    elif 'Loại thiết bị:' in line:
                        value = line.split(':', 1)[1].strip()
                        if value and value != 'Chưa có':
                            ticket_info['device_type'] = value
                    elif 'Nội dung sự cố:' in line:
                        value = line.split(':', 1)[1].strip()
                        if value and value != 'Chưa có':
                            ticket_info['problem_description'] = value
                
                # FIXED: Trả về ticket_info nếu có ít nhất một trường hợp lệ
                if len(ticket_info) > 0:
                    print(f"[CREATE DEBUG] Extracted ticket info: {ticket_info}")
                    return ticket_info
                    
            except Exception as e:
                print(f"[EXTRACT ERROR] {e}")
                continue
    
    print("[CREATE DEBUG] No ticket info found in history")
    return None

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
        print(f"[TICKET SAVED] ID: {ticket_id}")
        print(f"[TICKET DATA] {ticket_data}")
        
        return ticket_id
        
    except Exception as e:
        print(f"[SAVE ERROR] {e}")
        return f"ERROR_{datetime.now().strftime('%H%M%S')}"

# Translation mapping for user-friendly field names
field_translation = {
    'serial_number': 'S/N hoặc ID thiết bị',
    'device_type': 'Loại thiết bị',
    'problem_description': 'Nội dung sự cố'
}
