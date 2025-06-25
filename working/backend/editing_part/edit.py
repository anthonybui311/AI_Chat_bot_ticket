import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import re

# Internal imports
import working.backend.utility.utils as utils   
import working.configuration.config as config
import working.backend.api_part.api_call as api

# Configure module logger
logger = logging.getLogger(__name__)

# =====================================================
# CORE CONSTANTS AND CONFIGURATIONS
# =====================================================

# Ticket ID patterns for validation
TICKET_ID_PATTERNS = [
    r'^TK\d+$',  # TK123456
    r'^\d+$',    # 123456
    r'^[A-Z]{2}\d+$',  # AB123456
]

# Editable ticket fields
EDITABLE_FIELDS = {
    "summary": "mô tả",
    "status": "trạng thái"
}

# =====================================================
# MAIN STAGE HANDLER
# =====================================================

def handle_edit_stage(response_text, summary: str, stage_manager) -> Tuple[str, str]:
    """
    Main edit stage handler following 5-step workflow
    Args:
        response_text: AI response (can be dict or string)
        summary: Response summary/intent
        stage_manager: Stage management object
    Returns:
        Tuple of (final_response, final_summary)
    """
    try:
        logger.info(f"Edit stage - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: Switch to create mode
        if summary == 'tạo ticket':
            return _handle_switch_to_create()
        
        # Case 2: Exit system
        elif summary == 'thoát':
            return _handle_exit_request()
        
        # Case 3: Response contains ticket_id (dictionary) - Step 1: Ticket ID Input
        elif isinstance(response_text, dict):
            return _process_ticket_id_input(response_text, stage_manager)
        
        # Case 4: Response is informational string
        elif isinstance(response_text, str):
            return _handle_informational_response(response_text, summary)
        
        # Case 5: Fallback for unexpected response types
        else:
            logger.warning(f"Unexpected response type in edit stage: {type(response_text)}")
            return _handle_unexpected_response()
            
    except Exception as e:
        logger.error(f"Error in edit stage handler: {e}")
        return _handle_edit_error(e)

# =====================================================
# STEP 1: TICKET ID INPUT
# =====================================================

def _process_ticket_id_input(ticket_info: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    Step 1: Process ticket ID input and validate
    Args:
        ticket_info: Dictionary containing ticket_id
        stage_manager: Stage management object
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Step 1 - Processing ticket ID input: {list(ticket_info.keys())}")
        
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
# STEP 2: TICKET RETRIEVAL
# =====================================================

def _retrieve_ticket_for_editing(ticket_id, stage_manager) -> Tuple[str, str]:
    """
    Step 2: Retrieve ticket from database
    Args:
        ticket_id: Valid ticket ID
        stage_manager: Stage management object
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Step 2 - Retrieving ticket: {ticket_id}")
        
        # Fetch ticket from database using existing API
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
        
        # Store ticket data and proceed to step 3
        stage_manager.store_ticket_data({"ticket_id": ticket_id, "ticket_info": ticket})
        logger.info(f"Switching to updating ticket stage")
        stage_manager.switch_stage('updating_ticket')
        
        # Step 3: Display ticket information and request update selection
        return _display_and_request_update(ticket, ticket_id)
        
    except Exception as e:
        logger.error(f"Error retrieving ticket: {e}")
        return _handle_edit_error(e)

# =====================================================
# STEP 3: DISPLAY & UPDATE SELECTION
# =====================================================

def _display_and_request_update(ticket: Dict[str, Any], ticket_id: str) -> Tuple[str, str]:
    """
    Step 3: Display ticket info and request what to update
    Args:
        ticket: Ticket data from database
        ticket_id: Ticket ID
    Returns:
        Tuple of (response, summary)
    """
    try:
        # Format ticket information using existing function
        ticket_info = _format_ticket_info(ticket)
        
        response = f"""📋 Thông tin ticket {ticket_id}:
{ticket_info}

Đây là thông tin ticket. Bạn muốn cập nhật thông tin gì? Tôi có thể cập nhật mô tả và trạng thái của ticket.

Vui lòng cho biết:
- Trường cần cập nhật (mô tả hoặc trạng thái)
- Nội dung mới

Ví dụ: "cập nhật mô tả thành: máy in không in được màu"
"""
        
        logger.info(f"Displayed ticket {ticket_id} for editing")
        return response, "chờ thông tin cập nhật"
        
    except Exception as e:
        logger.error(f"Error displaying ticket for editing: {e}")
        return _handle_edit_error(e)

# =====================================================
# STEP 4: UPDATING TICKET STAGE HANDLER
# =====================================================

def handle_updating_ticket_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    Handle ticket updating stage - collects update data and transitions to confirmation
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
            return _handle_exit_request()
        
        # Case 2: Response contains update data (dictionary)
        elif isinstance(response_text, dict) and summary == 'cập nhật ticket':
            return _process_update_data(response_text, stage_manager)
        
        # Case 3: Response is informational string
        elif isinstance(response_text, str):
            if summary == 'chờ thông tin cập nhật':
                response, summary = _display_and_request_update(stage_manager.get_stored_ticket_data()['ticket_info'], stage_manager.get_stored_ticket_data()['ticket_id'])
                response_text += "\n" + response
                return response_text, summary
            return _handle_informational_response(response_text, summary)
        
        # Case 4: Fallback
        else:
            return _handle_unexpected_response()
            
    except Exception as e:
        logger.error(f"Error in updating ticket stage: {e}")
        return _handle_edit_error(e)

def _process_update_data(update_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    Process ticket update data and show confirmation
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
        
        # Store update data for confirmation
        stage_manager.store_ticket_data({
            **stored_data,
            "update_data": update_data
        })
        
        # Switch to confirmation stage
        stage_manager.switch_stage('edit_confirmation')
        
        # Display confirmation message
        return _display_update_confirmation(ticket_id, update_data)
        
    except Exception as e:
        logger.error(f"Error processing update data: {e}")
        return _handle_edit_error(e)

def _display_update_confirmation(ticket_id: str, update_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Display update confirmation to user
    Args:
        ticket_id: Ticket ID
        update_data: Update information
    Returns:
        Tuple of (response, summary)
    """
    try:
        # Format update information
        update_info = []
        for field, value in update_data.items():
            field_display = EDITABLE_FIELDS.get(field, field)
            update_info.append(f"• {field_display}: {value}")
        
        update_text = "\n".join(update_info)
        
        response = f"""✅ Xác nhận thông tin cập nhật cho ticket {ticket_id}:
{update_text}

Thông tin này có chính xác không?
(Trả lời 'đúng' để xác nhận hoặc 'sai' để nhập lại)"""
        
        return response, "chờ xác nhận cập nhật edit"
        
    except Exception as e:
        logger.error(f"Error displaying update confirmation: {e}")
        return _handle_edit_error(e)

# =====================================================
# STEP 4: EDIT CONFIRMATION STAGE HANDLER (NEW)
# =====================================================

def handle_edit_confirmation_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    Handle edit_confirmation stage - Step 4 of the workflow
    This is called when stage = 'edit_confirmation' and user responds with 'đúng' or 'sai'
    Args:
        stage_manager: Stage management object
        response_text: AI response
        summary: Response summary/intent ('đúng', 'sai', etc.)
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Edit confirmation stage - Summary: {summary}")
        
        # Case 1: User confirms update information is correct - proceed to Step 5
        if summary == 'đúng':
            return _handle_update_confirmation_correct(stage_manager)
        
        # Case 2: User says update information is wrong - return to Step 3
        elif summary == 'sai':
            return _handle_update_confirmation_wrong(stage_manager)
        
        # Case 3: User wants to exit
        elif summary == 'thoát':
            stage_manager.clear_ticket_data()
            return _handle_exit_request()
        
        # Case 4: Unexpected response
        else:
            response = "Vui lòng trả lời 'đúng' để xác nhận hoặc 'sai' để nhập lại thông tin."
            return response, "chờ xác nhận cập nhật edit"
            
    except Exception as e:
        logger.error(f"Error in edit confirmation stage: {e}")
        return _handle_edit_error(e)

# =====================================================
# STEP 5: UPDATE EXECUTION
# =====================================================

def _handle_update_confirmation_correct(stage_manager) -> Tuple[str, str]:
    """
    Step 5: Execute the update when user confirms
    Args:
        stage_manager: Stage management object
    Returns:
        Tuple of (response, summary)
    """
    try:
        stored_data = stage_manager.get_stored_ticket_data()
        if not stored_data or 'update_data' not in stored_data:
            logger.error("No update data found for execution")
            return _handle_edit_error(Exception("Missing update data"))
        
        ticket_id = stored_data['ticket_id']
        update_data = stored_data['update_data']
        
        # Execute the update using existing API
        return _execute_ticket_update(ticket_id, update_data, stage_manager)
        
    except Exception as e:
        logger.error(f"Error handling update confirmation correct: {e}")
        return _handle_edit_error(e)

def _execute_ticket_update(ticket_id: str, update_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    Execute ticket update via API
    Args:
        ticket_id: Ticket ID to update
        update_data: Update information
        stage_manager: Stage management object
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Executing update for ticket {ticket_id}")
        
        # Call API to update ticket using existing function
        result = api.post_update_ticket(ticket_id, update_data)
        
        # Handle API response
        if result and result.get('response_code') == 200:
            # Success - format response
            update_fields = ", ".join([EDITABLE_FIELDS.get(k, k) for k in update_data.keys()])
            response = f"""✅ Cập nhật ticket thành công!

📋 Thông tin đã cập nhật:
• Ticket ID: {ticket_id}
• Trường đã cập nhật: {update_fields}

Cảm ơn bạn đã sử dụng dịch vụ!"""
            
            # Clear data and reset to main
            stage_manager.clear_ticket_data()
            stage_manager.reset_to_main()
            return response, "thoát"
        else:
            # Failure - handle error
            return _handle_update_api_error(ticket_id, result if result else {})
            
    except Exception as e:
        logger.error(f"Error executing ticket update: {e}")
        return _handle_edit_error(e)

# =====================================================
# VALIDATION FUNCTIONS
# =====================================================

def validate_ticket_id(ticket_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate ticket information following create.py patterns
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
        logger.info(f"Ticket ID validation - Valid: {is_valid}, Missing fields: {missing_fields}")
        return is_valid, missing_fields
        
    except Exception as e:
        logger.error(f"Error validating ticket ID: {e}")
        return False, ['ticket_id']

def _is_valid_ticket_id_format(ticket_id: str) -> bool:
    """
    Check if ticket ID matches valid patterns
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
# DISPLAY AND FORMATTING FUNCTIONS
# =====================================================

def _format_ticket_info(ticket: Dict[str, Any]) -> str:
    """
    Format ticket information for display following existing patterns
    Args:
        ticket: Ticket data dictionary
    Returns:
        Formatted ticket information string
    """
    try:
        # Extract ticket fields with defaults
        ticket_id = ticket.get('ticketid', ticket.get('id', 'N/A'))
        summary = ticket.get('summary', 'Không có mô tả')
        status = ticket.get('status', 'N/A')
        
        # Build formatted string
        info_parts = f"""• ID: {ticket_id}
• Mô tả: {summary}
• Trạng thái: {status}"""
        
        return info_parts
        
    except Exception as e:
        logger.error(f"Error formatting ticket info: {e}")
        return "Không thể hiển thị thông tin ticket"

# =====================================================
# CONFIRMATION HANDLERS
# =====================================================

def _handle_update_confirmation_wrong(stage_manager) -> Tuple[str, str]:
    """Handle when user says update information is wrong"""
    try:
        # Return to step 3 - display and update selection
        stored_data = stage_manager.get_stored_ticket_data()
        if stored_data and 'ticket_info' in stored_data:
            ticket = stored_data['ticket_info']
            ticket_id = stored_data['ticket_id']
            
            # Remove update data and switch back to updating stage
            stage_manager.store_ticket_data({"ticket_id": ticket_id, "ticket_info": ticket})
            stage_manager.switch_stage('updating_ticket')
            logger.info(f"Switching back to updating ticket stage")
            
            return _display_and_request_update(ticket, ticket_id)
        else:
            logger.warning("No ticket data found for re-display")
            response = "Cảm ơn bạn đã phản hồi. Vui lòng cung cấp thông tin ticket ID để tiếp tục."
            return response, "sửa ticket"
            
    except Exception as e:
        logger.error(f"Error handling update confirmation wrong: {e}")
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

def _handle_exit_request() -> Tuple[str, str]:
    """Handle user exit request from edit mode"""
    response = ("Dạ vâng, vậy khi nào bạn có nhu cầu sửa ticket "
                "thì mình hỗ trợ bạn nhé. Chào tạm biệt bạn")
    return response, "thoát"

def _handle_informational_response(response_text: str, summary: str) -> Tuple[str, str]:
    """Handle informational string responses in edit mode"""
    return response_text, summary if summary else "sửa ticket"

def _handle_unexpected_response() -> Tuple[str, str]:
    """Handle unexpected response types in edit mode"""
    logger.warning("Received unexpected response type in edit stage")
    response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket. Vui lòng thử lại."
    return response, "sửa ticket"

def _handle_edit_error(error: Exception) -> Tuple[str, str]:
    """Handle edit stage errors following create.py patterns"""
    error_message = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu sửa ticket: {error}"
    return error_message, "thoát"

def _handle_incomplete_ticket_id(missing_fields: List[str]) -> Tuple[str, str]:
    """Handle incomplete ticket ID information"""
    try:
        missing_field = missing_fields[0] if missing_fields else "ticket_id"
        field_display = EDITABLE_FIELDS.get(missing_field, missing_field)
        
        if missing_field == 'invalid_ticket_id_format':
            response = "Ticket ID không đúng định dạng. Vui lòng cung cấp ticket ID hợp lệ (ví dụ: TK123456 hoặc 123456)."
        else:
            response = f"Thông tin sửa ticket còn thiếu: {field_display}. Vui lòng cung cấp thêm thông tin."
        
        logger.info(f"Incomplete ticket ID - missing: {missing_fields}")
        return response, "sửa ticket"
        
    except Exception as e:
        logger.error(f"Error handling incomplete ticket ID: {e}")
        return _handle_edit_error(e)

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
