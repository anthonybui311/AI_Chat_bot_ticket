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
import backend.api_call as api

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
            
        # Case 3: Response là dictionary (thông tin ticket_id)
        elif isinstance(response_text, dict):
            return process_edit_ticket_data(response_text, user_input, chain, chat_history)
            
        # Case 4: Response là string (phản hồi thông thường hoặc hướng dẫn)
        elif isinstance(response_text, str):
            return response_text, summary
        # Case 5: Fallback
        else:
            error_response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket. Vui lòng thử lại."
            return error_response, "sửa ticket"
            
    except Exception as e:
        print(f"[EDIT ERROR] {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket: {e}"
        return error_response, "thoát"

def process_edit_ticket_data(ticket_id, user_input, chain, chat_history):
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
    
    print(f"[EDIT DEBUG] Processing edit ticket data: {ticket_id}")
    
    # Validate ticket data
    is_complete, missing_fields = validate_ticket_id(ticket_id)
    
    if is_complete:
        # Ticket đầy đủ thông tin - Hiển thị để xác nhận\
        ticket_info = ticket_id["ticket_id"]
        ticket = api.get_ticket_by_id(ticket_info)
        if not ticket:
            print(f"[EDIT DEBUG] Ticket not found by ID - return ticket = {ticket}")
            response = f"""Em kiểm tra thông tin thì không thấy ticket_id {ticket_info} này trên hệ thống. Anh chị vui lòng kiểm tra lại thông tin và liên hệ lại sau. Em cảm ơn, em chào anh chị."""
            return response, "thoát"
        
        #TODO: Thêm logic xác nhận sửa ticket
        print(f"[EDIT DEBUG] Ticket found - return ticket = {ticket}")
        response = f"""Thông tin ticket như sau: {ticket_info}. Bạn cung cấp tôi thông tin nội dung bạn muốn sửa. Tôi sẽ tiến hành sửa ticket này cho bạn."""
        return response, "thêm nội dung sửa ticket"
        
    else:
        # Ticket thiếu thông tin - Yêu cầu bổ sung
        missing_fields_str = missing_fields[0]
        request_response = f"Thông tin sửa ticket còn thiếu: {missing_fields_str}. Vui lòng cung cấp thêm thông tin."
        return request_response, "sửa ticket"



def validate_ticket_id(ticket_id):
    """
    IMPROVED: Validate dữ liệu ticket trước khi lưu
    
    Args:
        ticket_id: Dictionary chứa thông tin ticket
        
    Returns:
        tuple: (bool, list)
        - bool: True nếu dữ liệu hợp lệ, False nếu có lỗi
        - list: Danh sách các trường còn thiếu
    """
    
    required_fields = ['ticket_id']
    
    if not isinstance(ticket_id, dict) or required_fields[0] not in ticket_id:
        return False, required_fields
    
    
    return True, []

