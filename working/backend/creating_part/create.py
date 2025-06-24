import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

# Internal imports
import working.backend.utils as utils
import working.configuration.config as config
import working.backend.api_call as api

# Configure module logger
logger = logging.getLogger(__name__)


# =====================================================
# CORE CONSTANTS AND CONFIGURATIONS
# =====================================================

# Field translation for user-friendly display
FIELD_TRANSLATION = {
    'serial_number': 'S/N hoặc ID thiết bị',
    'device_type': 'Loại thiết bị',
    'problem_description': 'Nội dung sự cố'
}

# Required fields for ticket creation
REQUIRED_TICKET_FIELDS = ['serial_number', 'device_type', 'problem_description']
# =====================================================
# MAIN STAGE HANDLER
# =====================================================

def handle_create_stage(response_text, summary: str, stage_manager) -> Tuple[str, str]:
    """
    OPTIMIZED: Comprehensive create stage handler with complete workflow
    
    Args:
        response_text: AI response (can be dict or string)
        summary: Response summary/intent
        user_input: Original user input
        chain: LangChain processing chain
        chat_history: Chat history object
        stage_manager: Stage management object
        
    Returns:
        Tuple of (final_response, final_summary)
    """
    try:
        logger.info(f"Create stage - Response type: {type(response_text)}, Summary: {summary}")
        
        # Case 1: User confirms information is correct
        if summary == 'đúng':
            return _handle_confirmation_correct(stage_manager)
            
        # Case 2: User says information is wrong
        elif summary == 'sai':
            return _handle_confirmation_wrong(stage_manager)
            
        # Case 3: Switch to edit mode
        elif summary == 'sửa ticket':
            return _handle_switch_to_edit()
            
        # Case 4: Exit system
        elif summary == 'thoát':
            return _handle_exit_request()
            
        # Case 5: Response contains ticket data (dictionary)
        elif isinstance(response_text, dict):
            return _process_ticket_data(response_text, stage_manager)
            
        # Case 6: Response is informational string
        elif isinstance(response_text, str):
            return _handle_informational_response(response_text, summary)
            
        # Case 7: Fallback for unexpected response types
        else:
            logger.warning(f"Unexpected response type: {type(response_text)}")
            return _handle_unexpected_response()
            
    except Exception as e:
        logger.error(f"Error in create stage handler: {e}")
        return _handle_creation_error(e)


# =====================================================
# CONFIRMATION HANDLERS
# =====================================================

def _handle_confirmation_correct(stage_manager) -> Tuple[str, str]:
    """Handle when user confirms ticket information is correct"""
    try:
        stored_ticket_data = stage_manager.get_stored_ticket_data()
        
        if stored_ticket_data:
            logger.info("User confirmed ticket data - proceeding to creation")
            response = "Cảm ơn bạn đã xác nhận. Hệ thống sẽ tiến hành tạo ticket ngay."
            return response, "đúng"
        else:
            logger.warning("No ticket data found for confirmation")
            response = ("Cảm ơn bạn! Tuy nhiên mình cần bạn cung cấp thông tin cụ thể "
                       "để tạo ticket: S/N hoặc ID thiết bị và nội dung sự cố. "
                       "Ví dụ: '12345, máy in hỏng'")
            return response, "tạo ticket"
            
    except Exception as e:
        logger.error(f"Error handling confirmation correct: {e}")
        return _handle_creation_error(e)


def _handle_confirmation_wrong(stage_manager) -> Tuple[str, str]:
    """Handle when user says ticket information is wrong"""
    try:
        stored_ticket_data = stage_manager.get_stored_ticket_data()
        if stored_ticket_data:
            stage_manager.clear_ticket_data()
            logger.info("User indicated wrong information - clearing data")
            response = ("Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin "
                       "chính xác để mình tạo ticket mới cho bạn.")
            return response, "tạo ticket"
        else:
            logger.warning("No ticket data found for confirmation")
            response = ("Cảm ơn bạn! Tuy nhiên mình cần bạn cung cấp thông tin cụ thể "
                       "để tạo ticket: S/N hoặc ID thiết bị và nội dung sự cố. "
                       "Ví dụ: '12345, máy in hỏng'")
            return response, "tạo ticket"
        
    except Exception as e:
        logger.error(f"Error handling confirmation wrong: {e}")
        return _handle_creation_error(e)


def _handle_switch_to_edit() -> Tuple[str, str]:
    """Handle request to switch to edit mode"""
    response = ("Đã chuyển sang chế độ sửa ticket cho bạn. "
               "Bạn muốn sửa nội dung ticket nào? "
               "Vui lòng cung cấp thông tin ticket ID.")
    return response, "sửa ticket"


def _handle_exit_request() -> Tuple[str, str]:
    """Handle user exit request"""
    response = ("Dạ vâng, vậy khi nào bạn có nhu cầu tạo ticket "
               "thì mình hỗ trợ bạn nhé. Chào tạm biệt bạn")
    return response, "thoát"


def _handle_informational_response(response_text: str, summary: str) -> Tuple[str, str]:
    """Handle informational string responses"""
    return response_text, summary if summary else "tạo ticket"


def _handle_unexpected_response() -> Tuple[str, str]:
    """Handle unexpected response types"""
    logger.warning("Received unexpected response type")
    response = "Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại."
    return response, "tạo ticket"


def _handle_creation_error(error: Exception) -> Tuple[str, str]:
    """Handle creation stage errors"""
    error_message = f"Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu tạo ticket: {error}"
    return error_message, "thoát"


# =====================================================
# TICKET DATA PROCESSING
# =====================================================

def _process_ticket_data(ticket_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    OPTIMIZED: Process ticket data with comprehensive validation
    
    Args:
        ticket_data: Dictionary containing ticket information
        stage_manager: Stage management object
        
    Returns:
        Tuple of (response, summary)
    """
    try:
        logger.info(f"Processing ticket data: {list(ticket_data.keys())}")
        
        # Validate and normalize ticket data
        normalized_data = _normalize_ticket_data(ticket_data)
        is_complete, missing_fields = validate_ticket_data(normalized_data)
        
        if is_complete:
            # Complete ticket data - store and show for confirmation
            return _handle_complete_ticket_data(normalized_data, stage_manager)
        else:
            # Incomplete ticket data - request missing information
            return _handle_incomplete_ticket_data(missing_fields)
            
    except Exception as e:
        logger.error(f"Error processing ticket data: {e}")
        return _handle_creation_error(e)


def _normalize_ticket_data(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    OPTIMIZED: Normalize and clean ticket data
    
    Args:
        ticket_data: Raw ticket data
        
    Returns:
        Normalized ticket data
    """
    try:
        normalized = {}
        
        # Normalize serial number
        serial = ticket_data.get('serial_number', '').strip()
        normalized['serial_number'] = serial
        
        # Normalize device type
        device_type = ticket_data.get('device_type', '').strip().lower()
        normalized['device_type'] = device_type
        
        # Normalize problem description
        problem = ticket_data.get('problem_description', '').strip()
        normalized['problem_description'] = problem
        
        logger.debug(f"Normalized ticket data: {normalized}")
        return normalized
        
    except Exception as e:
        logger.error(f"Error normalizing ticket data: {e}")
        return ticket_data


def _handle_complete_ticket_data(ticket_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """Handle complete ticket data"""
    try:
        # Additional validation for business rules
        validation_result = _validate_business_rules(ticket_data)
        if not validation_result['valid']:
            return validation_result['message'], "tạo ticket"
        
        # Store ticket data and create confirmation
        stage_manager.store_ticket_data(ticket_data)
        confirmation_response = format_ticket_confirmation(ticket_data)
        
        logger.info("Complete ticket data processed and stored")
        return confirmation_response, "chờ xác nhận"
        
    except Exception as e:
        logger.error(f"Error handling complete ticket data: {e}")
        return _handle_creation_error(e)


def _handle_incomplete_ticket_data(missing_fields: List[str]) -> Tuple[str, str]:
    """Handle incomplete ticket data"""
    try:
        # Create user-friendly field names
        missing_fields_display = [FIELD_TRANSLATION.get(field, field) for field in missing_fields]
        missing_fields_str = ", ".join(missing_fields_display)
        
        response = f"Thông tin ticket còn thiếu: {missing_fields_str}. Vui lòng cung cấp thêm thông tin."
        
        logger.info(f"Incomplete ticket data - missing: {missing_fields}")
        return response, "tạo ticket"
        
    except Exception as e:
        logger.error(f"Error handling incomplete ticket data: {e}")
        return _handle_creation_error(e)


def _validate_business_rules(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    OPTIMIZED: Validate business rules for ticket creation
    
    Args:
        ticket_data: Ticket data to validate
        
    Returns:
        Dictionary with validation result and message
    """
    try:
        # Check serial number format
        serial_number = ticket_data.get('serial_number', '')
        if len(serial_number) < 3:
            return {
                'valid': False,
                'message': 'Serial number quá ngắn. Vui lòng cung cấp Serial number có ít nhất 3 ký tự.'
            }
        
        # Check for suspicious patterns
        if _contains_suspicious_content(ticket_data):
            return {
                'valid': False,
                'message': 'Thông tin không hợp lệ. Vui lòng kiểm tra lại và cung cấp thông tin chính xác.'
            }
        
        return {'valid': True, 'message': ''}
        
    except Exception as e:
        logger.error(f"Error validating business rules: {e}")
        return {'valid': True, 'message': ''}  # Default to valid on error


def _contains_suspicious_content(ticket_data: Dict[str, Any]) -> bool:
    """Check for suspicious content in ticket data"""
    try:
        # List of suspicious patterns
        suspicious_patterns = ['test', 'dummy', 'fake', 'xxx', '000000']
        
        for field_value in ticket_data.values():
            if isinstance(field_value, str):
                field_lower = field_value.lower()
                if any(pattern in field_lower for pattern in suspicious_patterns):
                    if len(field_value.strip()) < 5:  # Only flag if very short
                        return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking suspicious content: {e}")
        return False


# =====================================================
# VALIDATION FUNCTIONS
# =====================================================

def validate_ticket_data(ticket_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    OPTIMIZED: Comprehensive ticket data validation
    
    Args:
        ticket_data: Dictionary containing ticket information
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    try:
        missing_fields = []
        
        for field in REQUIRED_TICKET_FIELDS:
            value = ticket_data.get(field, '')
            
            # Check if field exists and has meaningful content
            if not value or not str(value).strip():
                missing_fields.append(field)
                continue
            
        is_complete = len(missing_fields) == 0
        
        logger.info(f"Ticket validation - Complete: {is_complete}, Missing: {missing_fields}")
        return is_complete, missing_fields
        
    except Exception as e:
        logger.error(f"Error validating ticket data: {e}")
        return False, REQUIRED_TICKET_FIELDS.copy()


def format_ticket_confirmation(ticket_data: Dict[str, Any]) -> str:
    """
    OPTIMIZED: Format ticket information for user confirmation
    
    Args:
        ticket_data: Dictionary containing ticket information
        
    Returns:
        Formatted confirmation string
    """
    try:
        # Extract and sanitize data
        serial_number = ticket_data.get('serial_number', 'Chưa có')
        device_type = ticket_data.get('device_type', 'Chưa có')
        problem_description = ticket_data.get('problem_description', 'Chưa có')
        
        # Create formatted confirmation
        confirmation_text = f"""✅ Mình xin xác nhận thông tin như sau:

• S/N hoặc ID thiết bị: {serial_number}
• Loại thiết bị: {device_type}
• Nội dung sự cố: {problem_description}

Thông tin này có chính xác không ạ?
(Trả lời 'đúng' để xác nhận hoặc 'sai' để nhập lại, hoặc nhập lại thông tin cần sửa)"""

        logger.debug("Ticket confirmation formatted")
        return confirmation_text
        
    except Exception as e:
        logger.error(f"Error formatting ticket confirmation: {e}")
        return "Có lỗi xảy ra khi hiển thị thông tin ticket. Vui lòng thử lại."


# =====================================================
# DATABASE AND API INTEGRATION
# =====================================================
def check_ticket_on_database(ticket_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    OPTIMIZED: Check ticket against database with enhanced error handling
    
    Args:
        ticket_data: Dictionary containing ticket information
        
    Returns:
        List of CI data from database
    """
    try:
        serial_number = ticket_data.get('serial_number', '')
        
        if not serial_number:
            logger.warning("No serial number provided for database check")
            return []
        
        logger.info(f"Checking database for serial number: {serial_number}")
        
        # Query database for CI information
        ci_data = api.get_ci_with_sn(serial_number)
        
        if ci_data:
            logger.info(f"Found {len(ci_data)} CI records for serial: {serial_number}")
            return ci_data if isinstance(ci_data, list) else [ci_data]
        else:
            logger.info(f"No CI records found for serial: {serial_number}")
            return []
            
    except Exception as e:
        logger.error(f"Error checking ticket on database: {e}")
        # Return empty list on error to allow ticket creation
        return []


def get_existing_tickets_for_device(serial_number: str) -> List[Dict[str, Any]]:
    """
    OPTIMIZED: Get existing tickets for a device
    
    Args:
        serial_number: Device serial number
        
    Returns:
        List of existing tickets
    """
    try:
        if not serial_number:
            return []
        
        logger.info(f"Getting existing tickets for serial: {serial_number}")
        #TODO
        existing_tickets = api.get_all_ticket_for_sn(serial_number)
        
        if existing_tickets:
            logger.info(f"Found {len(existing_tickets)} existing tickets")
            return existing_tickets if isinstance(existing_tickets, list) else [existing_tickets]
        else:
            logger.info("No existing tickets found")
            return []
            
    except Exception as e:
        logger.error(f"Error getting existing tickets: {e}")
        return []

# =====================================================
# TICKET PROCESSING FUNCTIONS (MERGED AND OPTIMIZED)
# =====================================================

def _process_ticket_creation(ticket_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """Process ticket creation with CI data checking"""
    try:
        ci_data = check_ticket_on_database(ticket_data)
        
        if not ci_data:
            # No CI data found - create ticket directly
            return _create_ticket_directly(ticket_data)
        elif len(ci_data) == 1:
            # Single CI data found - process accordingly
            return _handle_single_ci_data_processing(ci_data[0], ticket_data, stage_manager)
        elif len(ci_data) > 1:
            # Multiple CI data found - ask user to clarify
            stage_manager.store_ci_data(ci_data)
            stage_manager.switch_stage('multiple_ci_data')
            return _handle_multiple_ci_data_display(ci_data)
        else:
            return _handle_ticket_creation_error()

    except Exception as e:
        logger.error(f"Error processing ticket creation: {e}")
        return _handle_ticket_creation_error()

def _handle_single_ci_data_processing(ci_data: Dict[str, Any], ticket_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    MERGED FUNCTION: Process single CI data (combines both previous functions)
    This function handles the core logic for processing a single CI data record
    """
    try:
        serial_number = ci_data.get('SerialNum', ci_data.get('serial_number', ''))
        device_name = ci_data.get('Name', ci_data.get('name', 'Unknown Device'))
        
        logger.info(f"Processing single CI data for S/N: {serial_number}")
        
        # Check for existing tickets
        existing_tickets = api.get_all_ticket_for_sn(serial_number)
        
        if existing_tickets:
            # Check ticket statuses
            active_tickets = []
            for ticket in existing_tickets:
                status = ticket.get('status', '').lower()
                if status not in ['resolved', 'closed', 'cancelled']:
                    active_tickets.append(ticket)
            
            if active_tickets:
                # Has active tickets - ask user for confirmation
                ticket_list = []
                for ticket in active_tickets[:3]:  # Show max 3 tickets
                    ticket_id = ticket.get('ticketid', 'N/A')
                    status = ticket.get('status', 'N/A')
                    summary = ticket.get('summary', 'No summary')[:50] + "..." if len(ticket.get('summary', '')) > 50 else ticket.get('summary', 'No summary')
                    ticket_list.append(f"#{ticket_id} ({status}): {summary}")
                
                tickets_text = "\n".join([f"• {ticket}" for ticket in ticket_list])
                
                response_text = f"""⚠️ Thiết bị "{device_name}" (S/N: {serial_number}) đã có ticket đang hoạt động:

{tickets_text}

Bạn có chắc chắn muốn tạo ticket mới không?
- Nhập 'có' hoặc 'tạo' để tạo ticket mới
- Nhập 'không' để hủy"""
                
                # Store data and switch to single CI data stage
                stage_manager.store_ci_data([ci_data])
                stage_manager.switch_stage('1_ci_data')
                return response_text, "1_ci_data"
            else:
                # All tickets are resolved/closed - create new ticket
                return _create_ticket_with_ci_data(ticket_data, ci_data, stage_manager)
        else:
            # No existing tickets - create new one
            return _handle_ticket_creation_error()

    except Exception as e:
        logger.error(f"Error processing single CI data: {e}")
        return _handle_ticket_creation_error()

def _handle_multiple_ci_data_display(ci_data_list: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    OPTIMIZED: Display multiple CI data with user clarification
    """
    try:
        ci_info = []
        for i, ci in enumerate(ci_data_list[:5], 1):  # Show max 5 CIs
            serial = ci.get('SerialNum', ci.get('serial_number', 'N/A'))
            name = ci.get('Name', ci.get('name', 'N/A'))
            location = ci.get('Location', ci.get('location', ''))
            
            location_text = f" - {location}" if location else ""
            ci_info.append(f"{i}. {name} (S/N: {serial}){location_text}")

        ci_list_text = "\n".join(ci_info)
        
        response = f"""🔍 Tìm thấy nhiều thiết bị với thông tin tương tự:

{ci_list_text}

Vui lòng cung cấp Serial Number chính xác để tạo ticket.
Ví dụ: '{ci_data_list[0].get('SerialNum', '123456')}' hoặc 'không' để hủy"""

        return response, "multiple_ci_data"

    except Exception as e:
        logger.error(f"Error displaying multiple CI data: {e}")
        return _handle_ticket_creation_error()

def _create_ticket_directly(ticket_data: Dict[str, Any]) -> Tuple[str, str]:
    """Create ticket directly when no CI conflicts"""
    try:
        summary = ticket_data['device_type'] + " " + ticket_data['problem_description'] if ticket_data['device_type'] not in ticket_data['problem_description'] else ticket_data['problem_description']
        ticket_id = api.post_create_ticket((ticket_data['serial_number']), summary)
        
        if ticket_id:
            response_text = f"✅ Ticket đã được tạo thành công! Mã ticket: {ticket_id}. Cảm ơn bạn đã liên hệ!"
            logger.info(f"Ticket created successfully: {ticket_id}")
            return response_text, "thoát"
        else:
            return _handle_ticket_creation_error()

    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return _handle_ticket_creation_error()

def _create_ticket_with_ci_data(ticket_data: Dict[str, Any], ci_data: Dict[str, Any], stage_manager) -> Tuple[str, str]:
    """
    OPTIMIZED: Create ticket with CI data information
    """
    try:
        serial_number = ci_data.get('SerialNum', ci_data.get('serial_number', ticket_data.get('serial_number', '')))
        device_name = ci_data.get('Name', ci_data.get('name', 'Unknown Device'))
        
        logger.info(f"Creating ticket for device: {device_name} (S/N: {serial_number})")
        
        # Create ticket via API
        ticket_id = api.post_create_ticket(serial_number, ticket_data.get('problem_description', 'N/A'))
        
        if ticket_id:
            response_text = f"""✅ Ticket đã được tạo thành công!

📋 Thông tin ticket:
• Mã ticket: {ticket_id}
• Thiết bị: {device_name}   
• Serial Number: {serial_number}
• Mô tả sự cố: {ticket_data.get('problem_description', 'N/A')}

Cảm ơn bạn đã liên hệ! Ticket sẽ được xử lý sớm nhất."""
            
            logger.info(f"Ticket created successfully: {ticket_id}")
            stage_manager.reset_to_main()
            return response_text, "thoát"
        else:
            return _handle_ticket_creation_error()

    except Exception as e:
        logger.error(f"Error creating ticket with CI data: {e}")
        return _handle_ticket_creation_error()

def _handle_ticket_creation_error() -> Tuple[str, str]:
    """Handle ticket creation errors"""
    response_text = "❌ Rất xin lỗi, hệ thống gặp sự cố và không thể tạo ticket. Vui lòng thử lại sau. Cảm ơn bạn!"
    return response_text, "thoát"

def _handle_cancel_ticket_creation() -> Tuple[str, str]:
    """Handle cancellation of ticket creation"""
    response_text = "Mình đã thực hiện hủy yêu cầu tạo phiếu của bạn rồi ạ. Cảm ơn bạn đã liên hệ, chào tạm biệt bạn!"
    return response_text, "thoát"

# =====================================================
# UPDATE HANDLING FUNCTIONS
# =====================================================

def _update_ticket_data(stage_manager, update_data, summary) -> Tuple[str, str]:
    """Update ticket data with new information"""
    try:
        current_ticket_data = stage_manager.get_stored_ticket_data()
        if not current_ticket_data:
            logger.error("No ticket data found for update")
            return "Không tìm thấy thông tin ticket để cập nhật.", "thoát"

        # Update ticket data
        updated_ticket_data = update_ticket_data(current_ticket_data, update_data)
        stage_manager.store_ticket_data(updated_ticket_data)

        # Create new confirmation response
        confirmation_response = format_ticket_confirmation(updated_ticket_data)
        logger.info("Ticket data updated successfully")
        
        #TODO: fix this
        # Switch back to confirmation stage
        stage_manager.switch_stage('create')
        return utils._handle_create_stage_routing(stage_manager, confirmation_response, "chờ xác nhận")

    except Exception as e:
        logger.error(f"Error updating ticket data: {e}")
        return "Có lỗi xảy ra khi cập nhật thông tin.", "error"

def update_ticket_data(current_data: Dict[str, Any], update_data) -> Dict[str, Any]:
    """
    OPTIMIZED: Update ticket data with new values
    """
    try:
        updated_data = current_data.copy()
        
        if isinstance(update_data, dict):
            if "field_to_update" in update_data and "new_value" in update_data:
                # Single field update
                field = update_data["field_to_update"]
                value = update_data["new_value"]
                if field in ['serial_number', 'device_type', 'problem_description']:
                    updated_data[field] = value
                    logger.info(f"Updated {field}: {current_data.get(field, 'N/A')} → {value}")
            else:
                # Multiple field updates
                for key, value in update_data.items():
                    if key in ['serial_number', 'device_type', 'problem_description']:
                        updated_data[key] = value
                        logger.info(f"Updated {key}: {current_data.get(key, 'N/A')} → {value}")

        return updated_data

    except Exception as e:
        logger.error(f"Error updating ticket data: {e}")
        return current_data
    


def _handle_confirmation_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    OPTIMIZED: Handle confirmation stage with full update capability
    """
    try:
        logger.info(f"Confirmation stage - Summary: {summary}")

        # Handle update requests
        update_keywords = ['cập nhật', 'sửa', 'thay đổi', 'đổi', 'chỉnh sửa', 'thành']
        if isinstance(response_text, dict):
            stage_manager.switch_stage('update_confirmation')
            return _handle_update_confirmation_stage(stage_manager, response_text, summary)
        # Handle confirmation actions
        if summary == 'đúng':
            stage_manager.switch_stage('correct')
            return _handle_correct_stage(stage_manager, response_text, 'đang xử lý')
        elif summary == 'sai':
            stage_manager.switch_stage('create')
            stage_manager.clear_ticket_data()
            return response_text, "tạo ticket"
        elif summary == 'thoát':
            stage_manager.reset_to_main()
            return response_text, "thoát"
        else:
            return response_text, "chờ xác nhận"

    except Exception as e:
        logger.error(f"Error in confirmation stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra trong quá trình xác nhận: {e}"
        return error_response, "error"

def _handle_update_confirmation_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """Handle update confirmation stage"""
    try:
        if summary == 'cập nhật thông tin':
            # Update ticket data and return to confirmation
            return _update_ticket_data(stage_manager, response_text, summary)
        elif summary == 'thoát':
            stage_manager.reset_to_main()
            return response_text, "thoát"
        else:
            return response_text, summary

    except Exception as e:
        logger.error(f"Error in update confirmation stage: {e}")
        return "Có lỗi xảy ra khi cập nhật thông tin.", "error"



def _handle_correct_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    OPTIMIZED: Handle correct stage (ticket processing)
    """
    try:
        logger.info(f"Correct stage - Summary: {summary}")
        
        if summary == 'đang xử lý':
            ticket_data = stage_manager.get_stored_ticket_data()
            if ticket_data:
                return _process_ticket_creation(ticket_data, stage_manager)
            else:
                return _handle_ticket_creation_error()
        elif summary == 'hoàn thành':
            stage_manager.reset_to_main()
            return response_text, "ticket đã được tạo"
        elif summary == 'thoát':
            stage_manager.reset_to_main()
            return response_text, summary
        else:
            return response_text, summary

    except Exception as e:
        logger.error(f"Error in correct stage: {e}")
        error_response = f"Xin lỗi, có lỗi xảy ra trong quá trình xử lý ticket: {e}"
        return error_response, "error"

def _handle_single_ci_data_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    MERGED FUNCTION: Handle single CI data stage (formerly _handle_one_ci_data_stage)
    This function handles both single CI data scenarios and user confirmation for ticket creation
    """
    try:
        logger.info(f"Single CI data stage - Summary: {summary}")
        
        if summary == 'tạo':
            # User wants to create ticket - proceed with creation
            ticket_data = stage_manager.get_stored_ticket_data()
            ci_data = stage_manager.get_stored_ci_data()
            
            if ticket_data and ci_data:
                return _create_ticket_with_ci_data(ticket_data, ci_data[0], stage_manager)
            else:
                return _handle_ticket_creation_error()
                
        elif summary == 'Không tạo':
            # User doesn't want to create ticket
            stage_manager.reset_to_main()
            return _handle_cancel_ticket_creation()
            
        elif summary == 'thoát':
            stage_manager.reset_to_main()
            return response_text, "thoát"
            
        else:
            return response_text, summary

    except Exception as e:
        logger.error(f"Error in single CI data stage: {e}")
        return _handle_ticket_creation_error()

def _handle_multiple_ci_data_stage(stage_manager, response_text, summary: str) -> Tuple[str, str]:
    """
    OPTIMIZED: Handle multiple CI data stage
    """
    try:
        logger.info(f"Multiple CI data stage - Summary: {summary}")
        
        if summary == 'kiểm tra serial number':
            # User provided a specific serial number
            serial_number = response_text  # The AI should return the serial number
            ci_data_list = stage_manager.get_stored_ci_data()
            
            if ci_data_list:
                # Find matching CI data
                selected_ci = None
                for ci in ci_data_list:
                    if ci.get('SerialNum') == serial_number or ci.get('serial_number') == serial_number:
                        selected_ci = ci
                        break
                
                if selected_ci:
                    ticket_data = stage_manager.get_stored_ticket_data()
                    if ticket_data:
                        return _handle_single_ci_data_processing(selected_ci, ticket_data, stage_manager)
                    else:
                        return _handle_ticket_creation_error()
                else:
                    return "Serial number không tìm thấy trong danh sách. Vui lòng chọn lại.", "multiple_ci_data"
            else:
                return _handle_ticket_creation_error()
                
        elif summary == 'Không tạo':
            # User doesn't want to create ticket
            stage_manager.reset_to_main()
            return _handle_cancel_ticket_creation()
            
        elif summary == 'thoát':
            stage_manager.reset_to_main()
            return response_text, "thoát"
            
        else:
            return response_text, summary

    except Exception as e:
        logger.error(f"Error in multiple CI data stage: {e}")
        return _handle_ticket_creation_error()