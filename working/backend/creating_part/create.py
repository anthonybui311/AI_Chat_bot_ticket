# create.py

"""
Module xử lý logic tạo ticket.
KHÔNG lấy input trực tiếp từ người dùng.
Chỉ nhận dữ liệu từ start.py, xử lý và trả về kết quả.
"""

import backend.starting_part.start as start
import backend.utils as utils
import configuration.config as config
import backend.editing_part.edit as edit
import json

def create_ticket(chain, chat_history, user_input, context, response_text, summary, ticket_data):
    """
    Xử lý logic tạo ticket dựa trên input đã nhận từ start.py
    
    Args:
        chain: Chuỗi xử lý LangChain đã được khởi tạo
        chat_history: Đối tượng ChatHistory để duy trì lịch sử hội thoại
        user_input: Input của người dùng đã được lấy từ start.py
        context: Ngữ cảnh cho AI
    
    Returns:
        tuple: (response_text, summary, ticket_data) - Phản hồi cho người dùng và ý định tiếp theo
    """
    
    # Gọi AI để xử lý input trong ngữ cảnh tạo ticket
    try:
        if summary==None:  # Nếu như hàm get_response bị lỗi parse, trả lại summary là tạo ticket và response gốc
            summary = "tạo ticket"
        
        # Xử lý khi AI trả về thông báo ticket đã được ghi nhận
        if response_text == "Thông tin ticket đã được ghi nhận. Vui lòng chờ xử lý." and ticket_data:
            try:
                # Parse ticket_data nếu nó là string JSON
                if isinstance(ticket_data, str):
                    python_ticket_data = json.loads(ticket_data)
                else:
                    python_ticket_data = ticket_data
                
                print(f"Debug - Ticket data: {python_ticket_data}")
                
                check_ticket, missing_fields = validate_ticket_data(python_ticket_data)
                
                if check_ticket:
                    response_text = f"""Mình xin xác nhận thông tin như sau:
                                        S/N hoặc ID thiết bị: {python_ticket_data.get('serial_number', 'Chưa có')}
                                        Loại thiết bị: {python_ticket_data.get('device_type', 'Chưa có')}
                                        Nội dung sự cố: {python_ticket_data.get('problem_description', 'Chưa có')}

                                        đúng không ạ?"""
                    summary = "tạo ticket"
                else:
                    missing_fields_str = ", ".join(missing_fields)
                    response_text = f"Thông tin ticket còn bị thiếu. Vui lòng cung cấp thông tin còn thiếu là {missing_fields_str}."
                    summary = "tạo ticket"
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing ticket_data JSON: {e}")
                response_text = "Có lỗi xảy ra khi xử lý thông tin ticket. Vui lòng thử lại."
                summary = "tạo ticket"
        
        return response_text, summary, ticket_data
        
    except Exception as e:
        print(f"Error in create_ticket: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu tạo ticket. Lỗi: {e}"
        return error_response, "tạo ticket", None  # Giữ nguyên trạng thái tạo ticket

def validate_ticket_data(ticket_data):
    """
    Validate dữ liệu ticket trước khi lưu, bao gồm kiểm tra nhập nhầm trường
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
    
    Returns:
        tuple: (bool, list)
        - bool: True nếu dữ liệu hợp lệ (đầy đủ và đúng), False nếu có lỗi
        - list: Danh sách các trường còn thiếu hoặc rỗng
    """
    
    # Các trường bắt buộc
    required_fields = ['serial_number', 'device_type', 'problem_description']
    
    # Tất cả các trường hợp lệ
    missing_fields = []
    
    # Kiểm tra ticket_data có phải là dictionary không
    if not isinstance(ticket_data, dict):
        return False, required_fields
    
    # Kiểm tra các trường bắt buộc
    for field in required_fields:
        if field not in ticket_data or not str(ticket_data[field]).strip():
            missing_fields.append(field)
    
    # Ticket hợp lệ khi không thiếu trường bắt buộc
    is_valid = len(missing_fields) == 0
    
    return is_valid, missing_fields

def save_ticket_to_database(ticket_data):
    """
    Lưu ticket vào database (ví dụ - chưa implement)
    
    Args:
        ticket_data: Dictionary chứa thông tin ticket
    
    Returns:
        str: ID của ticket đã tạo hoặc None nếu lỗi
    """
    # TODO: Implement database saving logic
    pass
