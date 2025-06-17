# edit.py

"""
Module xử lý logic sửa ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
Tương tự như create.py nhưng cho chức năng edit ticket.
"""

import backend.utils as utils
import configuration.config as config
import json
from datetime import datetime

def handle_edit_stage(response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý toàn bộ logic cho edit stage
    
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
        print(f"[EDIT DEBUG] Processing - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: Chuyển sang create stage
        if summary == 'tạo ticket':
            return response_text, summary
            
        # Case 2: Thoát khỏi hệ thống
        elif summary == 'thoát':
            return response_text, summary
            
        # Case 3: Response là dictionary (thông tin ticket được sửa)
        elif isinstance(response_text, dict):
            return process_edit_ticket_data(response_text, user_input, chain, chat_history)
            
        # Case 4: Response là string (phản hồi thông thường hoặc hướng dẫn)
        elif isinstance(response_text, str):
            return process_edit_string_response(response_text, summary, user_input, chain, chat_history)
            
        # Case 5: Fallback
        else:
            error_response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket. Vui lòng thử lại."
            return error_response, "sửa ticket"
            
    except Exception as e:
        print(f"[EDIT ERROR] {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket: {e}"
        return error_response, "system_error"

def process_edit_ticket_data(ticket_data, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý khi response là dictionary chứa thông tin ticket đã sửa
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket đã sửa
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    print(f"[EDIT DEBUG] Processing edit ticket data: {ticket_data}")
    
    # Validate ticket data
    is_complete, missing_fields = validate_edit_ticket_data(ticket_data)
    
    if is_complete:
        # Ticket đầy đủ thông tin - Hiển thị để xác nhận
        confirmation_response = format_edit_ticket_confirmation(ticket_data)
        return confirmation_response, "awaiting_edit_confirmation"
    else:
        # Ticket thiếu thông tin - Yêu cầu bổ sung
        missing_fields_str = ", ".join([field_translation.get(f, f) for f in missing_fields])
        request_response = f"Thông tin sửa ticket còn thiếu: {missing_fields_str}. Vui lòng cung cấp thêm thông tin."
        return request_response, "sửa ticket"

def process_edit_string_response(response_text, summary, user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý khi response là string trong edit stage
    
    Args:
        response_text: String response từ AI
        summary: Tóm tắt ý định
        user_input: Input gốc của người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    # Kiểm tra xem có phải là phản hồi xác nhận không
    if is_edit_confirmation_response(user_input):
        return handle_edit_ticket_confirmation(user_input, chain, chat_history)
    
    # Trả về response gốc với summary tương ứng
    return response_text, summary if summary else "sửa ticket"

def handle_edit_ticket_confirmation(user_input, chain, chat_history):
    """
    NEW FUNCTION: Xử lý phản hồi xác nhận sửa ticket từ người dùng
    
    Args:
        user_input: Input xác nhận từ người dùng
        chain: LangChain chain
        chat_history: Lịch sử chat
        
    Returns:
        tuple: (response, summary)
    """
    
    # Phân tích input xác nhận
    confirmation_keywords_positive = ['đúng', 'chính xác', 'ok', 'yes', 'correct', 'phải', 'vâng', 'ừ', 'lưu']
    confirmation_keywords_negative = ['sai', 'không chính xác', 'không ok', 'no', 'incorrect', 'không phải', 'không đúng']
    
    user_input_lower = user_input.lower()
    
    # Xác nhận ĐÚNG - Lưu ticket đã sửa
    if any(keyword in user_input_lower for keyword in confirmation_keywords_positive):
        # Lấy thông tin ticket từ lịch sử chat gần đây nhất
        ticket_info = extract_edit_ticket_from_history(chat_history)
        
        if ticket_info:
            # Cập nhật ticket (placeholder)
            ticket_id = ticket_info.get('ticket_id', 'UNKNOWN')
            update_result = update_ticket_in_database(ticket_id, ticket_info)
            
            if update_result:
                success_response = f"Ticket {ticket_id} đã được cập nhật thành công. Cảm ơn bạn đã sử dụng dịch vụ!"
                return success_response, "ticket_edited"
            else:
                error_response = "Có lỗi xảy ra khi cập nhật ticket. Vui lòng thử lại."
                return error_response, "sửa ticket"
        else:
            error_response = "Không thể tìm thấy thông tin ticket để cập nhật. Vui lòng thử lại."
            return error_response, "sửa ticket"
    
    # Xác nhận SAI - Yêu cầu nhập lại
    elif any(keyword in user_input_lower for keyword in confirmation_keywords_negative):
        retry_response = "Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin chính xác để mình sửa ticket cho bạn."
        return retry_response, "sửa ticket"
    
    # Không rõ ràng - Hỏi lại
    else:
        clarify_response = "Mình chưa hiểu ý bạn. Thông tin sửa ticket trên có chính xác không? Vui lòng trả lời 'đúng' hoặc 'sai'."
        return clarify_response, "awaiting_edit_confirmation"

def validate_edit_ticket_data(ticket_data):
    """
    NEW FUNCTION: Validate dữ liệu ticket đã sửa
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket đã sửa
        
    Returns:
        tuple: (bool, list)
        - bool: True nếu dữ liệu hợp lệ, False nếu có lỗi
        - list: Danh sách các trường còn thiếu
    """
    
    required_fields = ['ticket_id']  # Ticket ID là bắt buộc để edit
    optional_fields = ['serial_number', 'device_type', 'problem_description']
    missing_fields = []
    
    if not isinstance(ticket_data, dict):
        return False, required_fields + optional_fields
    
    # Kiểm tra ticket_id (bắt buộc)
    ticket_id = ticket_data.get('ticket_id', '')
    if not ticket_id or not str(ticket_id).strip():
        missing_fields.append('ticket_id')
    
    # Kiểm tra ít nhất một trường cần sửa phải có giá trị
    has_edit_content = False
    for field in optional_fields:
        value = ticket_data.get(field, '')
        if value and str(value).strip():
            has_edit_content = True
            break
    
    if not has_edit_content:
        missing_fields.extend(optional_fields)
    
    return len(missing_fields) == 0, missing_fields

def format_edit_ticket_confirmation(ticket_data):
    """
    NEW FUNCTION: Format thông tin ticket đã sửa để xác nhận
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket đã sửa
        
    Returns:
        str: Chuỗi thông tin ticket được format
    """
    
    ticket_id = ticket_data.get('ticket_id', 'Chưa có')
    serial_number = ticket_data.get('serial_number', 'Không thay đổi')
    device_type = ticket_data.get('device_type', 'Không thay đổi')
    problem_description = ticket_data.get('problem_description', 'Không thay đổi')
    
    confirmation_text = f"""Mình xin xác nhận thông tin sửa ticket như sau:

• Ticket ID: {ticket_id}
• S/N hoặc ID thiết bị: {serial_number}
• Loại thiết bị: {device_type}
• Nội dung sự cố: {problem_description}

Thông tin này có chính xác không ạ?"""
    
    return confirmation_text

def is_edit_confirmation_response(user_input):
    """
    NEW FUNCTION: Kiểm tra xem input có phải là phản hồi xác nhận edit không
    
    Args:
        user_input: Input của người dùng
        
    Returns:
        bool: True nếu là phản hồi xác nhận
    """
    
    confirmation_indicators = [
        'đúng', 'sai', 'chính xác', 'không chính xác', 'ok', 'không ok',
        'yes', 'no', 'correct', 'incorrect', 'phải', 'không phải',
        'vâng', 'không', 'ừ', 'uh huh', 'đồng ý', 'không đồng ý', 'lưu'
    ]
    
    user_input_lower = user_input.lower().strip()
    
    # Kiểm tra input ngắn (1-3 từ) có chứa từ khóa xác nhận
    words = user_input_lower.split()
    if len(words) <= 3:
        return any(indicator in user_input_lower for indicator in confirmation_indicators)
    
    return False

def extract_edit_ticket_from_history(chat_history):
    """
    NEW FUNCTION: Trích xuất thông tin ticket đã sửa từ lịch sử chat
    
    Args:
        chat_history: Đối tượng ChatHistory
        
    Returns:
        dict: Thông tin ticket hoặc None nếu không tìm thấy
    """
    
    # Tìm trong các tin nhắn AI gần đây nhất để tìm thông tin ticket
    messages = chat_history.get_messages()
    
    # Duyệt ngược từ tin nhắn gần nhất
    for message in reversed(messages):
        if hasattr(message, 'content') and 'Ticket ID:' in message.content:
            # Parse thông tin ticket từ message content
            try:
                lines = message.content.split('\n')
                ticket_info = {}
                
                for line in lines:
                    if 'Ticket ID:' in line:
                        ticket_info['ticket_id'] = line.split(':')[1].strip()
                    elif 'S/N hoặc ID thiết bị:' in line:
                        value = line.split(':')[1].strip()
                        if value != 'Không thay đổi':
                            ticket_info['serial_number'] = value
                    elif 'Loại thiết bị:' in line:
                        value = line.split(':')[1].strip()
                        if value != 'Không thay đổi':
                            ticket_info['device_type'] = value
                    elif 'Nội dung sự cố:' in line:
                        value = line.split(':')[1].strip()
                        if value != 'Không thay đổi':
                            ticket_info['problem_description'] = value
                
                return ticket_info if 'ticket_id' in ticket_info else None
                
            except Exception as e:
                print(f"[EXTRACT EDIT ERROR] {e}")
                continue
    
    return None

def update_ticket_in_database(ticket_id, ticket_data):
    """
    NEW FUNCTION: Cập nhật ticket trong database (placeholder implementation)
    
    Args:
        ticket_id: ID của ticket cần cập nhật
        ticket_data: Dictionary chứa thông tin ticket mới
        
    Returns:
        bool: True nếu cập nhật thành công, False nếu có lỗi
    """
    
    try:
        # TODO: Implement actual database update logic
        # For now, just log the update operation
        
        print(f"[TICKET UPDATED] ID: {ticket_id}")
        print(f"[UPDATE DATA] {ticket_data}")
        print(f"[UPDATE TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Simulate successful update
        return True
        
    except Exception as e:
        print(f"[UPDATE ERROR] {e}")
        return False

# Translation mapping for user-friendly field names (same as create.py)
field_translation = {
    'ticket_id': 'Ticket ID',
    'serial_number': 'S/N hoặc ID thiết bị',
    'device_type': 'Loại thiết bị',
    'problem_description': 'Nội dung sự cố'
}
