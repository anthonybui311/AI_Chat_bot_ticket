import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import re

# Internal imports
import backend.utils as utils
import configuration.config as config
import backend.api_call as api

# Configure module logger
logger = logging.getLogger(__name__)

# =====================================================
# CORE CONSTANTS AND CONFIGURATIONS
# =====================================================

# Ticket ID patterns for validation
TICKET_ID_PATTERNS = [
    r'^TK\d+$',        # TK123456
    r'^\d+$',          # 123456
    r'^[A-Z]{2}\d+$',  # AB123456
]

# Editable ticket fields
EDITABLE_FIELDS = {
    "summary": "mô tả",
    "session_id": "session_id",
    "status": "trạng thái"
}

# =====================================================
# MAIN STAGE HANDLER
# =====================================================

def handle_edit_stage(response_text, summary: str, stage_manager) -> Tuple[str, str]:
    """
    OPTIMIZED: Comprehensive edit stage handler with complete workflow
    
    Args:
        response_text: AI response (can be dict or string)
        summary: Response summary/intent
        stage_manager: Stage management object
        
    Returns:
        Tuple of (final_response, final_summary)
    """
    try:
        logger.info(f"Edit stage - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: User confirms information is correct
        if summary == 'đúng':
            return _handle_edit_confirmation_correct(stage_manager)
            
        # Case 2: User says information is wrong
        elif summary == 'sai':
            return _handle_edit_confirmation_wrong(stage_manager)
        
        # Case 3: Switch to create mode
        elif summary == 'tạo ticket':
            return _handle_switch_to_create()
            
        # Case 4: Exit system
        elif summary == 'thoát':
            return _handle_edit_exit_request()
            
        # Case 5: Response contains ticket_id (dictionary) - Stage 1: Input Processing
        elif isinstance(response_text, dict):
            return _process_ticket_id_input(response_text, stage_manager)
            
        # Case 6: Response is informational string
        elif isinstance(response_text, str):
            return _handle_edit_informational_response(response_text, summary)
            
        # Case 7: Fallback for unexpected response types
        else:
            logger.warning(f"Unexpected response type in edit stage: {type(response_text)}")
            return _handle_edit_unexpected_response()
            
    except Exception as e:
        logger.error(f"Error in edit stage handler: {e}")
        return _handle_edit_error(e)

# =====================================================
# STAGE 1: INPUT PROCESSING (TICKET ID)
# =====================================================

def _process_ticket_id_input(ticket_info: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    Stage 1: Process ticket ID input and validate
    
    Args:
        ticket_info: Dictionary containing ticket_id
        stage_manager: Stage management object
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Stage 1 - Processing ticket ID input: {list(ticket_info.keys())}")
        
        # Validate ticket ID
        is_valid, missing_fields = validate_ticket_id(ticket_info)
        
        if is_valid:
            ticket_id = ticket_info.get("ticket_id", "")
            return _retrieve_ticket_for_editing(ticket_id, stage_manager)
        else:
            return _handle_incomplete_ticket_id(missing_fields)
            
    except Exception as e:
        logger.error(f"Error processing ticket ID input: {e}")
        return _handle_edit_error(e)

# =====================================================
# STAGE 2: TICKET RETRIEVAL
# =====================================================

def _retrieve_ticket_for_editing(ticket_id, stage_manager) -> Tuple[str, str]:
    """
    Stage 2: Retrieve ticket from database and display for editing
    
    Args:
        ticket_id: Valid ticket ID
        stage_manager: Stage management object
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Stage 2 - Retrieving ticket: {ticket_id}")
        
        # Fetch ticket from database
        ticket_data = api.get_ticket_by_id(ticket_id)
        
        if not ticket_data:
            return _handle_ticket_not_found(ticket_id)
        
        # Handle list or single ticket response
        if isinstance(ticket_data, list):
            if len(ticket_data) == 0:
                return _handle_ticket_not_found(ticket_id)
            ticket = ticket_data[0] #type: ignore
        else:
            ticket = ticket_data
        
        # Store ticket data and switch to updating stage
        stage_manager.store_ticket_data({"ticket_id": ticket_id, "ticket_info": ticket})
        logger.info(f"Switching to updating ticket stage")
        stage_manager.switch_stage('updating_ticket')
        
        # Display ticket information and request what to update
        return _display_ticket_for_editing(ticket, ticket_id)
        
    except Exception as e:
        logger.error(f"Error retrieving ticket: {e}")
        return _handle_edit_error(e)

# =====================================================
# STAGE 3: UPDATING TICKET STAGE HANDLER
# =====================================================

def handle_updating_ticket_stage(response_text, summary: str, stage_manager) -> Tuple[str, str]:
    """
    Stage 3: Handle ticket updating stage
    
    Args:
        response_text: AI response (dict with update data or string)
        summary: Response summary/intent
        stage_manager: Stage management object
        
    Returns:
        Tuple of (final_response, final_summary)
    """
    try:
        logger.info(f"Updating ticket stage - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: Exit system
        if summary == 'thoát':
            stage_manager.clear_ticket_data()
            return _handle_edit_exit_request()
            
        # Case 2: Response contains update data (dictionary)
        elif isinstance(response_text, dict) and summary == 'cập nhật ticket':
            return _process_ticket_update_data(response_text, stage_manager)
            
        # Case 3: Response is informational string
        elif isinstance(response_text, str):
            return _handle_edit_informational_response(response_text, summary)
            
        # Case 4: Fallback
        else:
            return _handle_edit_unexpected_response()
            
    except Exception as e:
        logger.error(f"Error in updating ticket stage: {e}")
        return _handle_edit_error(e)

def _process_ticket_update_data(update_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    Process ticket update data and apply changes
    
    Args:
        update_data: Dictionary containing update information
        stage_manager: Stage management object
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        # Get stored ticket data
        stored_data = stage_manager.get_stored_ticket_data()
        if not stored_data or 'ticket_id' not in stored_data:
            logger.error("No ticket data found for update")
            return _handle_edit_error(Exception("Missing ticket data"))
        
        ticket_id = stored_data['ticket_id']
        
        # Apply the update
        return _apply_ticket_update(ticket_id, update_data)
        
    except Exception as e:
        logger.error(f"Error processing update data: {e}")
        return _handle_edit_error(e)

def _apply_ticket_update(ticket_id: str, update_info: Dict[str, Any]) -> Tuple[str, str]:
    """
    OPTIMIZED: Apply ticket update to database
    
    Args:
        ticket_id: Ticket ID to update
        update_info: Update information
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        
        logger.info(f"Applying update to ticket {ticket_id}")
        
        # Call API to update ticket
        result = api.post_update_ticket(ticket_id, update_info)
        
        # Handle API response
        if result and result.get('response_code') == 200:
            response = f"""✅ Mình đã cập nhật thông tin ticket thành công!

📋 Thông tin cập nhật:
• Ticket ID: {ticket_id}
• Trường đã cập nhật: {update_info.keys()}
• Giá trị mới: {update_info.values()}

Cảm ơn bạn đã sử dụng dịch vụ! """
            
            return response, "thoát"
        else:
            return _handle_update_api_error(ticket_id, result if result else {})
            
    except Exception as e:
        logger.error(f"Error applying ticket update: {e}")
        return _handle_edit_error(e)

# =====================================================
# DISPLAY AND FORMATTING FUNCTIONS
# =====================================================

def _display_ticket_for_editing(ticket: Dict[str, Any], ticket_id: str) -> Tuple[str, str]:
    """
    OPTIMIZED: Display ticket information and request edit details
    
    Args:
        ticket: Ticket data from database
        ticket_id: Ticket ID
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        # Format ticket information
        ticket_info = _format_ticket_info(ticket)
        
        response = f"""Thông tin ticket {ticket_id}:

{ticket_info}

Bạn muốn cập nhật thông tin gì? Vui lòng cho biết:

- Trường cần cập nhật (ví dụ: mô tả, trạng thái, độ ưu tiên)
- Nội dung mới

Ví dụ: "cập nhật mô tả thành: máy in không in được màu"

"""
        
        logger.info(f"Displayed ticket {ticket_id} for editing")
        return response, "chờ thông tin cập nhật"
        
    except Exception as e:
        logger.error(f"Error displaying ticket for editing: {e}")
        return _handle_edit_error(e)

def _format_ticket_info(ticket: Dict[str, Any]) -> str:
    """
    OPTIMIZED: Format ticket information for display
    
    Args:
        ticket: Ticket data dictionary
        
    Returns:
        Formatted ticket information string
    """
    try:
        # Extract ticket fields with defaults
        ticket_id = ticket.get('ticketid', ticket.get('id', 'N/A'))
        session_id = ticket.get('sessionid', 'N/A')
        summary = ticket.get('summary', 'Không có mô tả')
        status = ticket.get('status', 'N/A')
        
        # Build formatted string
        info_parts = f"""• ID: {ticket_id}
• Session ID: {session_id}
• Mô tả: {summary}
• Trạng thái: {status}"""
        
        return info_parts
        
    except Exception as e:
        logger.error(f"Error formatting ticket info: {e}")
        return "Không thể hiển thị thông tin ticket"

# =====================================================
# VALIDATION FUNCTIONS
# =====================================================

def validate_ticket_id(ticket_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    OPTIMIZED: Validate ticket information
    
    Args:
        ticket_info: Dictionary containing ticket information
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    try:
        required_field = 'ticket_id'
        
        missing_fields = []
        
        if required_field not in ticket_info:
            missing_fields.append('ticket_id')
        
        # Additional validation for ticket ID format
        if not missing_fields:
            ticket_id = ticket_info['ticket_id']
            # Check if ticket ID is valid format
            if not _is_valid_ticket_id_format(ticket_id):
                missing_fields.append('invalid_ticket_id_format')
        
        is_valid = len(missing_fields) == 0
        logger.info(f"Ticket ID validation - Valid: {is_valid}, Missing or error fields: {missing_fields}")
        
        return is_valid, missing_fields
        
    except Exception as e:
        logger.error(f"Error validating ticket ID: {e}")
        return False, ['ticket_id']

def _is_valid_ticket_id_format(ticket_id: str) -> bool:
    """
    OPTIMIZED: Check if ticket ID matches valid patterns
    
    Args:
        ticket_id: Ticket ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    try:
        if not ticket_id or not isinstance(ticket_id, str):
            return False
        
        ticket_id = ticket_id.strip()
        
        # Check against known patterns
        for pattern in TICKET_ID_PATTERNS:
            if re.match(pattern, ticket_id, re.IGNORECASE):
                logger.debug(f"Ticket ID {ticket_id} matches pattern {pattern}")
                return True
        
        # Additional flexible pattern for alphanumeric IDs
        if ticket_id.replace('-', '').replace('_', '').isalnum():
            logger.debug(f"Ticket ID {ticket_id} matches alphanumeric pattern")
            return True
        
        logger.warning(f"Ticket ID {ticket_id} does not match any valid pattern")
        return False
        
    except Exception as e:
        logger.error(f"Error validating ticket ID format: {e}")
        return False

# =====================================================
# CONFIRMATION HANDLERS
# =====================================================
def _handle_edit_confirmation_correct(stage_manager) -> Tuple[str, str]:
    """Handle when user confirms ticket information is correct"""
    try:
        stored_ticket_data = stage_manager.get_stored_ticket_data()
        
        if stored_ticket_data and stage_manager.get_current_stage() == 'updating_ticket':
            logger.info("User confirmed ticket data - proceeding to creation")
            response = "Cảm ơn bạn đã xác nhận. Hệ thống sẽ tiến hành tạo ticket ngay."
            return response, "đúng"
        else:
            logger.warning("No ticket data found for confirmation")
            response = ("""Cảm ơn bạn đã phản hồi. Tuy nhiên mình cần bạn cung cấp thông tin cụ thể 
                       để sửa ticket. Bạn có thể sửa mô tả và trạng thái ticket. 
                       Ví dụ: 'cập nhật mô tả thành: máy in không in được màu'""")
            return response, "sửa ticket"
            
    except Exception as e:
        logger.error(f"Error handling confirmation correct: {e}")
        return _handle_edit_error(e)


def _handle_edit_confirmation_wrong(stage_manager) -> Tuple[str, str]:
    """Handle when user says ticket information is wrong"""
    try:
        stored_ticket_data = stage_manager.get_stored_ticket_data()
        if stored_ticket_data:
            stage_manager.clear_ticket_data()
            logger.info("User indicated wrong information - clearing data")
            response = ("""Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin 
                       chính xác để mình sửa ticket  cho bạn.""")
            return response, "sửa ticket"
        else:
            logger.warning("No ticket data found for confirmation")
            response = ("""Cảm ơn bạn đã phản hồi. Tuy nhiên mình cần bạn cung cấp thông tin cụ thể 
                       để sửa ticket. Bạn có thể sửa mô tả và trạng thái ticket. 
                       Ví dụ: 'cập nhật mô tả thành: máy in không in được màu'""")
            return response, "sửa ticket"
        
    except Exception as e:
        logger.error(f"Error handling confirmation wrong: {e}")
        return _handle_edit_error(e)

# =====================================================
# ERROR HANDLING FUNCTIONS
# =====================================================

def _handle_switch_to_create() -> Tuple[str, str]:
    """Handle request to switch to create mode"""
    response = ("Đã chuyển sang chế độ tạo ticket mới cho bạn. "
                "Để tạo ticket mới, bạn cần cung cấp thông tin sau: "
                "S/N hoặc ID thiết bị và nội dung sự cố.")
    return response, "tạo ticket"

def _handle_edit_exit_request() -> Tuple[str, str]:
    """Handle user exit request from edit mode"""
    response = ("Dạ vâng, vậy khi nào bạn có nhu cầu sửa ticket "
                "thì mình hỗ trợ bạn nhé. Chào tạm biệt bạn")
    return response, "thoát"

def _handle_edit_informational_response(response_text: str, summary: str) -> Tuple[str, str]:
    """Handle informational string responses in edit mode"""
    return response_text, summary if summary else "sửa ticket"

def _handle_edit_unexpected_response() -> Tuple[str, str]:
    """Handle unexpected response types in edit mode"""
    logger.warning("Received unexpected response type in edit stage")
    response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket. Vui lòng thử lại."
    return response, "sửa ticket"

def _handle_edit_error(error: Exception) -> Tuple[str, str]:
    """Handle edit stage errors"""
    error_message = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket: {error}"
    return error_message, "thoát"

def _handle_incomplete_ticket_id(missing_fields: List[str]) -> Tuple[str, str]:
    """Handle incomplete ticket ID information"""
    try:
        missing_field = missing_fields[0] if missing_fields else "ticket_id"
        field_display = EDITABLE_FIELDS.get(missing_field, missing_field)
        response = f"Thông tin sửa ticket còn thiếu: {field_display}. Vui lòng cung cấp thêm thông tin."
        logger.info(f"Incomplete ticket ID - missing: {missing_fields}")
        return response, "sửa ticket"
    except Exception as e:
        logger.error(f"Error handling incomplete ticket ID: {e}")
        return _handle_edit_error(e)

def _handle_invalid_ticket_format(ticket_id: str) -> Tuple[str, str]:
    """Handle invalid ticket ID format"""
    response = (f"Ticket ID '{ticket_id}' không đúng định dạng. "
                f"Vui lòng cung cấp ticket ID hợp lệ (ví dụ: TK123456 hoặc 123456).")
    return response, "sửa ticket"

def _handle_ticket_not_found(ticket_id: str) -> Tuple[str, str]:
    """Handle ticket not found in system"""
    response = (f"❌ Không tìm thấy ticket '{ticket_id}' trên hệ thống. "
                f"Vui lòng kiểm tra lại thông tin và thử lại sau. "
                f"Cảm ơn bạn!")
    return response, "thoát"

def _handle_update_api_error(ticket_id: str, result: Dict[str, Any]) -> Tuple[str, str]:
    """Handle API update error"""
    error_code = result.get('response_code', 'Unknown')
    error_message = result.get('message', 'Unknown error')
    response = f"❌ Không thể cập nhật ticket {ticket_id}. " \
               f"Lỗi hệ thống: {error_code} - {error_message}. " \
               f"Vui lòng thử lại sau."
    return response, "thoát"
