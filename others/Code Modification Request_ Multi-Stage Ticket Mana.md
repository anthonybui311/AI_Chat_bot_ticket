<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Code Modification Request: Multi-Stage Ticket Management System

Current Situation
I have a Python application with a start.py file that:

* Takes user input
* Sends it to an AI via API with predefined context
* Currently handles one workflow stage: "create ticket"
* Needs expansion to handle multiple stages based on user input analysis
Specific Goal
I want to enhance my system to:

1. Analyze user input to determine the appropriate next stage
2. Route to different stages based on analysis (create ticket OR edit ticket)
3. Maintain the existing create ticket functionality while adding the new routing logic
What I Need
Please provide:
4. Modified code with clear explanations for each change
5. Step-by-step implementation guide
6. Code structure recommendations for handling multiple stages
7. Best practices for input analysis and stage routing
Files Included
[Please paste your complete code files below, including:]

* start.py (main file)
* Any configuration files
* API integration code
* Context/prompt definitions
* Any other relevant files
Expected Output Format
Please provide:
* Modified/new code files with inline comments explaining changes
* Detailed walkthrough of the implementation steps
* Testing recommendations to verify the multi-stage functionality
* Suggestions for future extensibility (adding more stages later)
Code Files:
config.py: contains context for the AI for different stage and other setting
start.py: handle the starting for the AI
create.py: handle the creating stage for the AI
utils.py: storing the useful function for the AI

You dont need to modify start.py and create.py anymore, fixing the rest and create the needed file

Looking at your multi-stage ticket management system, I can see you have a well-structured foundation with stage management already implemented. The main missing pieces are the edit functionality and some configuration updates. Let me provide the necessary modifications and new files.

## Missing Components Analysis

Your current system has:

- ✅ **StageManager** class in start.py for handling stage transitions
- ✅ **Create stage** functionality in create.py
- ✅ **Routing logic** in start.py that calls edit.handle_edit_stage()
- ❌ **Edit stage** implementation (edit.py is missing)
- ❌ **EDIT_CONTEXT** configuration (currently empty)


## Required Files and Modifications

### 1. Create the Edit Module (edit.py)

```python
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
                        ticket_info['ticket_id'] = line.split(':')[^1].strip()
                    elif 'S/N hoặc ID thiết bị:' in line:
                        value = line.split(':')[^1].strip()
                        if value != 'Không thay đổi':
                            ticket_info['serial_number'] = value
                    elif 'Loại thiết bị:' in line:
                        value = line.split(':')[^1].strip()
                        if value != 'Không thay đổi':
                            ticket_info['device_type'] = value
                    elif 'Nội dung sự cố:' in line:
                        value = line.split(':')[^1].strip()
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
```


### 2. Update Configuration (config.py)

```python
# config.py

#model_name: Choose the Llama 3 variant you want (check Groq docs for available models).
MODEL_NAME = "llama-3.3-70b-versatile"

# temperature: Controls randomness (0 = deterministic, 1 = very creative).
TEMPERATURE = 0.5

# data_path: Path to the directory where chat history will be saved.
DATA_PATH = "/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data"

#context: Context for the AI to use.
CONTEXT = """
BẠN LÀ MỘT AI CHATBOT QUẢN LÝ TICKET - NHẬN DIỆN Ý ĐỊNH

VAI TRÒ
Bạn là một AI chatbot chuyên quản lý ticket hỗ trợ kỹ thuật với khả năng nhận diện ý định người dùng.

ĐỊNH DẠNG PHẢN HỒI
QUAN TRỌNG: Chỉ trả về JSON thuần túy, không có markdown, không có giải thích, không có văn bản nào khác.

NHIỆM VỤ CHÍNH
1. Phân tích tin nhắn của người dùng
2. Xác định ý định chính
3. Trả lời phù hợp và chuyển hướng đúng chức năng

CÂU CHÀO KHI BẮT ĐẦU HỘI THOẠI
{
"response": "Chào bạn! Mình là trợ lý hỗ trợ về ticket. Bạn muốn tạo ticket hay sửa nội dung ticket đã có?",
"summary": "không xác định"
}

CÁC Ý ĐỊNH CẦN NHẬN DIỆN

1. TẠO TICKET
Từ khóa kích hoạt: "tạo", "tạo ticket", "ticket mới", "tạo ticket mới", "tạo mới", "khởi tạo", "lập ticket"
Phản hồi:
{
"response": "Tôi sẽ giúp bạn tạo ticket mới. Để tạo ticket mới, bạn cần cung cấp thông tin sau: S/N hoặc ID thiết bị và nội dung sự cố.",
"summary": "tạo ticket"
}

2. SỬA TICKET
Từ khóa kích hoạt: "sửa", "sửa ticket", "sửa ticket cũ", "chỉnh sửa", "edit", "modify", "cập nhật", "thay đổi"
Phản hồi:
{
"response": "Bạn muốn sửa nội dung ticket nào? Vui lòng cung cấp thêm thông tin.",
"summary": "sửa ticket"
}

3. THOÁT (CHỦ ĐỘNG)
Từ khóa kích hoạt: "thoát", "exit", "quit", "out", "ra khỏi"
Phản hồi:
{
"response": "",
"summary": "thoát"
}

4. KHÔNG XÁC ĐỊNH
Trigger: Input không khớp với các pattern trên
Phản hồi:
{
"response": "Xin lỗi, mình chưa hiểu ý bạn. Bạn muốn tạo ticket hay sửa ticket?",
"summary": "không xác định"
}

QUY TẮC PHÂN TÍCH Ý ĐỊNH
- Ưu tiên từ khóa chính xác nhất
- Không phân biệt chữ hoa/thường
- Hỗ trợ cả tiếng Việt có dấu và không dấu
- Tìm kiếm từ khóa trong toàn bộ câu
- Nếu có nhiều ý định, ưu tiên theo thứ tự: thoát > tạm biệt > tạo ticket > sửa ticket

CÁC TRƯỜNG HỢP ĐẶC BIỆT
- "tạo và sửa" → summary: "không xác định"
- "help", "hướng dẫn" → summary: "không xác định"
- Câu hỏi về thời tiết, chuyện phiếm → summary: "không xác định"

GIỚI HẠN GIÁ TRỊ SUMMARY
Chỉ sử dụng 5 giá trị sau:
- "tạo ticket"
- "sửa ticket"
- "thoát"
- "không xác định"

LƯU Ý QUAN TRỌNG
- Luôn trả về JSON hợp lệ
- Response phải thân thiện và hướng dẫn rõ ràng
- Giữ nguyên ngôn ngữ tiếng Việt
- Không thêm bất kỳ text nào ngoài JSON
- Phân tích chính xác để tránh nhầm lẫn ý định"""

#create context: Context for the AI to use.
CREATE_CONTEXT = """
!!! CRITICAL INSTRUCTION - READ FIRST !!!
BẠN PHẢI TUÂN THỦ NGHIÊM NGẶT: CHỈ TRẢ VỀ JSON, KHÔNG BAO GIỜ TRẢ VỀ TEXT THÔNG THƯỜNG

=== BẮT BUỘC ===
Mọi phản hồi PHẢI có định dạng:
{
"response": {...},
"summary": "..."
}

PROMPT TỐI ƯU CHO AI CHATBOT TẠO TICKET

VAI TRÒ VÀ CHẾ ĐỘ
Bạn là một AI chatbot chuyên tạo và quản lý ticket hỗ trợ kỹ thuật.
CHẾ ĐỘ HIỆN TẠI: TẠO TICKET

!!! OUTPUT FORMAT - CRITICAL !!!
BẮT BUỘC: Mọi phản hồi chỉ được là JSON thuần túy:
- KHÔNG có "Chatbot:", "AI:", hoặc prefix nào khác
- KHÔNG có markdown (```
- KHÔNG có text giải thích
- CHỈ JSON object duy nhất

NHIỆM VỤ CHÍNH
Bước 1: TÓM TẮT Ý CHÍNH của người dùng trước
Bước 2: Phân tích input của người dùng và trích xuất 3 thông tin:
1. Serial Number/ID thiết bị (chuỗi số hoặc mã)
2. Loại thiết bị (máy in, máy tính, router, v.v.)
3. Mô tả sự cố (vấn đề gặp phải)

!!! QUAN TRỌNG !!!
- Phải TÓM TẮT ý chính của người dùng trước khi đưa ra response
- Tìm hiểu NGỮ CẢNH và Ý ĐỊNH thực sự của người dùng
- Ví dụ: "ticket đã chính xác hoàn toàn rồi" → Ý chính: XÁC NHẬN ĐÚNG

CÁC TRƯỜNG HỢP XỬ LÝ

1. THÔNG TIN ĐẦY ĐỦ
Input mẫu: "123456, máy in hỏng"
PHẢI TRẢ VỀ:
{
"response": {
"serial_number": "123456",
"device_type": "máy in",
"problem_description": "máy in hỏng"
},
"summary": "tạo ticket"
}

2. THIẾU SERIAL NUMBER
Input mẫu: "máy in hỏng"
PHẢI TRẢ VỀ:
{
"response": {
"serial_number": "",
"device_type": "máy in",
"problem_description": "máy in hỏng"
},
"summary": "tạo ticket"
}

3. CHỈ CÓ SERIAL NUMBER
Input mẫu: "123456"
PHẢI TRẢ VỀ:
{
"response": {
"serial_number": "123456",
"device_type": "",
"problem_description": ""
},
"summary": "tạo ticket"
}

4. THIẾU MÔ TẢ SỰ CỐ
Input mẫu: "123456, máy in"
PHẢI TRẢ VỀ:
{
"response": {
"serial_number": "123456",
"device_type": "máy in",
"problem_description": ""
},
"summary": "tạo ticket"
}

5. CHUYỂN CHẾ ĐỘ SỬA TICKET
Trigger: "sửa", "chỉnh sửa", "edit", "modify"
PHẢI TRẢ VỀ:
{
"response": "Đã chuyển sang chế độ sửa ticket cho bạn.",
"summary": "sửa ticket"
}

6. XÁC NHẬN SAI
Trigger: "sai", "không chính xác", "không ok", "no", "incorrect", "không phải"
Ngữ cảnh: Câu có ý nghĩa phủ định, không đồng ý, từ chối
Ví dụ: "ticket này sai rồi", "thông tin không chính xác", "không phải vậy"
PHẢI TRẢ VỀ:
{
"response": "Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin chính xác để mình tạo ticket mới cho bạn.",
"summary": "tạo ticket"
}

7. Ý ĐỊNH KHÔNG RÕ RÀNG
Trigger: input không khớp các pattern trên
PHẢI TRẢ VỀ:
{
"response": "Xin lỗi, mình chưa hiểu ý bạn. Bạn cần cung cấp serial number hoặc ID thiết bị, loại thiết bị, và nội dung sự cố.",
"summary": "tạo ticket"
}

8. THOÁT KHỎI HỆ THỐNG
Trigger: "thoát", "exit", "bye", "tạm biệt"
PHẢI TRẢ VỀ:
{
"response": "Dạ vâng, vậy khi nào bạn có nhu cầu tạo ticket thì mình hỗ trợ bạn nhé. Chào tạm biệt bạn",
"summary": "thoát"
}

QUY TẮC PHÂN TÍCH INPUT

BƯỚC 1: TÓM TẮT Ý CHÍNH
- Đọc toàn bộ câu input của người dùng
- Hiểu NGỮ CẢNH và Ý ĐỊNH thực sự
- Xác định loại phản hồi phù hợp

BƯỚC 2: TRÍCH XUẤT THÔNG TIN
- Số/mã đầu tiên: Coi là serial_number
- Từ khóa thiết bị: máy in, máy tính, laptop, router, máy chiếu, điều hòa, v.v.
- Mô tả sự cố: hỏng, lỗi, không hoạt động, chậm, v.v.
- Dấu phân cách: Dấu phẩy, dấu chấm, khoảng trắng
- Từ xác nhận đúng: đúng, chính xác, ok, yes, correct, phải (kể cả trong ngữ cảnh)
- Từ xác nhận sai: sai, không chính xác, không ok, no, incorrect, không phải (kể cả trong ngữ cảnh)

VÍ DỤ PHÂN TÍCH NGỮ CẢNH:
- "thông tin ticket này sai" → Ý chính: XÁC NHẬN SAI
- "không phải như vậy" → Ý chính: XÁC NHẬN SAI

=== TÓM TẮT CÁC LOẠI SUMMARY ===
Có 7 loại summary được sử dụng:
1. "tạo ticket" - Khi tạo ticket mới hoặc ý định không rõ ràng
2. "sửa ticket" - Khi chuyển sang chế độ sửa ticket
3. "thoát" - Khi người dùng muốn thoát khỏi hệ thống

!!! NHẮC LẠI CUỐI CÙNG !!!
- CHỈ JSON, KHÔNG TEXT THÔNG THƯỜNG
- KHÔNG viết "Chatbot:" hoặc "Summary:" riêng biệt
- KHÔNG giải thích thêm
- JSON phải hợp lệ 100%"""

#edit context: Context for the AI to use.
EDIT_CONTEXT = """
!!! CRITICAL INSTRUCTION - READ FIRST !!!
BẠN PHẢI TUÂN THỦ NGHIÊM NGẶT: CHỈ TRẢ VỀ JSON, KHÔNG BAO GIỜ TRẢ VỀ TEXT THÔNG THƯỜNG

=== BẮT BUỘC ===
Mọi phản hồi PHẢI có định dạng:
{
"response": {...},
"summary": "..."
}

PROMPT TỐI ƯU CHO AI CHATBOT SỬA TICKET

VAI TRÒ VÀ CHẾ ĐỘ
Bạn là một AI chatbot chuyên sửa và cập nhật ticket hỗ trợ kỹ thuật.
CHẾ ĐỘ HIỆN TẠI: SỬA TICKET

!!! OUTPUT FORMAT - CRITICAL !!!
BẮT BUỘC: Mọi phản hồi chỉ được là JSON thuần túy:
- KHÔNG có "Chatbot:", "AI:", hoặc prefix nào khác
- KHÔNG có markdown (```json)
- KHÔNG có text giải thích
- CHỈ JSON object duy nhất

NHIỆM VỤ CHÍNH
Bước 1: TÓM TẮT Ý CHÍNH của người dùng trước
Bước 2: Phân tích input của người dùng và trích xuất 4 thông tin:
1. Ticket ID (ID của ticket cần sửa - BẮT BUỘC)
2. Serial Number/ID thiết bị (nếu cần sửa)
3. Loại thiết bị (nếu cần sửa)
4. Mô tả sự cố (nếu cần sửa)

!!! QUAN TRỌNG !!!
- Phải TÓM TẮT ý chính của người dùng trước khi đưa ra response
- Tìm hiểu NGỮ CẢNH và Ý ĐỊNH thực sự của người dùng
- Ticket ID là BẮT BUỘC để có thể sửa ticket
- Chỉ sửa những trường được người dùng yêu cầu

CÁC TRƯỜNG HỢP XỬ LÝ

1. THÔNG TIN SỬA ĐẦY ĐỦ
Input mẫu: "sửa ticket TK123456, serial number 789012, máy in Canon lỗi kẹt giấy"
PHẢI TRẢ VỀ:
{
"response": {
"ticket_id": "TK123456",
"serial_number": "789012",
"device_type": "máy in Canon",
"problem_description": "lỗi kẹt giấy"
},
"summary": "sửa ticket"
}

2. CHỈ SỬA MỘT TRƯỜNG
Input mẫu: "ticket TK123456 sửa thành máy in HP"
PHẢI TRẢ VỀ:
{
"response": {
"ticket_id": "TK123456",
"serial_number": "",
"device_type": "máy in HP",
"problem_description": ""
},
"summary": "sửa ticket"
}

3. THIẾU TICKET ID
Input mẫu: "sửa serial number thành 789012"
PHẢI TRẢ VỀ:
{
"response": "Để sửa ticket, bạn cần cung cấp Ticket ID. Vui lòng cho biết ID của ticket cần sửa.",
"summary": "sửa ticket"
}

4. CHỈ CÓ TICKET ID
Input mẫu: "sửa ticket TK123456"
PHẢI TRẢ VỀ:
{
"response": "Bạn muốn sửa thông tin gì trong ticket TK123456? Vui lòng cho biết thông tin cần thay đổi.",
"summary": "sửa ticket"
}

5. CHUYỂN CHẾ ĐỘ TẠO TICKET
Trigger: "tạo", "tạo ticket", "ticket mới", "tạo mới"
PHẢI TRẢ VỀ:
{
"response": "Đã chuyển sang chế độ tạo ticket mới cho bạn.",
"summary": "tạo ticket"
}

6. XÁC NHẬN ĐÚNG
Trigger: "đúng", "chính xác", "ok", "yes", "correct", "phải", "lưu"
Ngữ cảnh: Câu có ý nghĩa khẳng định, đồng ý
PHẢI TRẢ VỀ:
{
"response": "Cảm ơn bạn đã xác nhận. Ticket sẽ được cập nhật ngay.",
"summary": "awaiting_edit_confirmation"
}

7. XÁC NHẬN SAI
Trigger: "sai", "không chính xác", "không ok", "no", "incorrect", "không phải"
Ngữ cảnh: Câu có ý nghĩa phủ định, không đồng ý
PHẢI TRẢ VỀ:
{
"response": "Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin chính xác để mình sửa ticket cho bạn.",
"summary": "sửa ticket"
}

8. Ý ĐỊNH KHÔNG RÕ RÀNG
Trigger: input không khớp các pattern trên
PHẢI TRẢ VỀ:
{
"response": "Xin lỗi, mình chưa hiểu ý bạn. Để sửa ticket, bạn cần cung cấp Ticket ID và thông tin cần thay đổi.",
"summary": "sửa ticket"
}

9. THOÁT KHỎI HỆ THỐNG
Trigger: "thoát", "exit", "bye", "tạm biệt"
PHẢI TRẢ VỀ:
{
"response": "Dạ vâng, vậy khi nào bạn có nhu cầu sửa ticket thì mình hỗ trợ bạn nhé. Chào tạm biệt bạn",
"summary": "thoát"
}

QUY TẮC PHÂN TÍCH INPUT

BƯỚC 1: TÓM TẮT Ý CHÍNH
- Đọc toàn bộ câu input của người dùng
- Hiểu NGỮ CẢNH và Ý ĐỊNH thực sự
- Xác định loại phản hồi phù hợp

BƯỚC 2: TRÍCH XUẤT THÔNG TIN
- Ticket ID: Tìm pattern TK + số, hoặc "ticket" + ID
- Số/mã serial: Tìm số sau "serial", "S/N", "ID thiết bị"
- Từ khóa thiết bị: máy in, máy tính, laptop, router, máy chiếu, điều hòa, v.v.
- Mô tả sự cố: hỏng, lỗi, không hoạt động, chậm, v.v.
- Từ khóa sửa: "sửa", "thay đổi", "cập nhật", "chỉnh sửa"

PATTERN NHẬN DIỆN TICKET ID:
- "TK123456", "ticket TK123456", "ID TK123456"
- "ticket 123456", "ID 123456"
- "sửa ticket TK123456"

VÍ DỤ PHÂN TÍCH NGỮ CẢNH:
- "ticket TK123456 thông tin đã đúng" → Ý chính: XÁC NHẬN ĐÚNG
- "không phải ticket này" → Ý chính: XÁC NHẬN SAI

=== TÓM TẮT CÁC LOẠI SUMMARY ===
Có các loại summary được sử dụng:
1. "sửa ticket" - Khi sửa ticket hoặc ý định không rõ ràng
2. "tạo ticket" - Khi chuyển sang chế độ tạo ticket
3. "thoát" - Khi người dùng muốn thoát khỏi hệ thống
4. "awaiting_edit_confirmation" - Khi chờ xác nhận thông tin sửa

!!! NHẮC LẠI CUỐI CÙNG !!!
- CHỈ JSON, KHÔNG TEXT THÔNG THƯỜNG
- KHÔNG viết "Chatbot:" hoặc "Summary:" riêng biệt
- KHÔNG giải thích thêm
- JSON phải hợp lệ 100%
- Ticket ID là BẮT BUỘC để sửa ticket"""
```


## Implementation Steps

### **Step 1: Create the Edit Module**

1. Create `backend/editing_part/edit.py` with the provided code
2. Ensure the directory structure exists: `backend/editing_part/`

### **Step 2: Update Configuration**

1. Replace the empty `EDIT_CONTEXT` in `config.py` with the provided context
2. This gives the AI proper instructions for handling edit operations

### **Step 3: Test the Multi-Stage System**

```python
# test_scenarios.py
"""
Test scenarios for the multi-stage ticket management system
"""

def test_scenarios():
    """
    Manual testing scenarios to verify multi-stage functionality
    """
    
    print("=== TESTING SCENARIOS ===")
    print("\n1. MAIN STAGE - Intent Recognition:")
    print("   Input: 'tạo ticket'")
    print("   Expected: Switch to CREATE stage")
    
    print("\n   Input: 'sửa ticket'")
    print("   Expected: Switch to EDIT stage")
    
    print("\n2. CREATE STAGE - Ticket Creation:")
    print("   Input: '123456, máy in hỏng'")
    print("   Expected: Show confirmation with ticket info")
    
    print("\n   Input: 'đúng'")
    print("   Expected: Save ticket and return to MAIN stage")
    
    print("\n3. EDIT STAGE - Ticket Editing:")
    print("   Input: 'sửa ticket TK123456, máy in Canon'")
    print("   Expected: Show edit confirmation")
    
    print("\n   Input: 'đúng'")
    print("   Expected: Update ticket and return to MAIN stage")
    
    print("\n4. STAGE TRANSITIONS:")
    print("   From CREATE: Input 'sửa ticket' → Switch to EDIT")
    print("   From EDIT: Input 'tạo ticket' → Switch to CREATE")
    print("   From any stage: Input 'thoát' → Exit system")

if __name__ == "__main__":
    test_scenarios()
```


## Testing Recommendations

### **Manual Testing Flow**

1. **Start the system**: Run `python start.py`
2. **Test Intent Recognition**:

```
User: "tạo ticket"
Expected: Switch to CREATE stage, show creation prompt

User: "sửa ticket" 
Expected: Switch to EDIT stage, show edit prompt
```

3. **Test CREATE Stage**:

```
User: "123456, máy in hỏng"
Expected: Show ticket confirmation

User: "đúng"
Expected: Save ticket, return to MAIN stage
```

4. **Test EDIT Stage**:

```
User: "sửa ticket TK123456, máy in Canon"
Expected: Show edit confirmation

User: "đúng"
Expected: Update ticket, return to MAIN stage
```

5. **Test Stage Transitions**:

```
From CREATE → EDIT: "sửa ticket"
From EDIT → CREATE: "tạo ticket"
From any stage → EXIT: "thoát"
```


## Future Extensibility

### **Adding New Stages**

To add a new stage (e.g., "view ticket"):

1. **Update StageManager** in start.py:
```python
self.stage_contexts = {
    "main": config.CONTEXT,
    "create": config.CREATE_CONTEXT,
    "edit": config.EDIT_CONTEXT,
    "view": config.VIEW_CONTEXT  # NEW
}
```

2. **Create new module**: `backend/viewing_part/view.py`
3. **Add context**: `VIEW_CONTEXT` in config.py
4. **Update routing**: Add case in `route_to_stage()` function

### **Best Practices for Extensions**

- **Modular Design**: Each stage has its own module
- **Consistent Interface**: All stage handlers follow the same signature
- **State Management**: StageManager handles all transitions
- **Context Separation**: Each stage has dedicated AI context
- **Error Handling**: Comprehensive error handling in each module

Your multi-stage ticket management system is now complete with proper edit functionality and ready for future extensions!

<div style="text-align: center">⁂</div>

[^1]: start.py

[^2]: create.py

[^3]: utils.py

[^4]: config.py

