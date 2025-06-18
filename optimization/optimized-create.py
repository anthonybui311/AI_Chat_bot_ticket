# create.py - Optimized Ticket Creation Module
"""
OPTIMIZED TICKET CREATION MODULE

This module handles all ticket creation workflows and logic.
Responsibilities:
- Process ticket creation requests
- Validate ticket information
- Handle confirmation workflows
- Integrate with database and API systems
- Manage multi-device scenarios

OPTIMIZATION IMPROVEMENTS:
- Complete workflow implementation for all cases
- Enhanced input validation and error handling
- Better integration with utils.py functions
- Comprehensive logging and debugging support
- Modular function design for easier maintenance
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime

# Internal imports
import backend.utils as utils
import configuration.config as config
import backend.api_call as api

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

# Device type mappings for normalization
DEVICE_TYPE_MAPPINGS = {
    'máy in': 'printer',
    'máy tính': 'computer',
    'laptop': 'laptop',
    'điện thoại': 'phone',
    'router': 'router',
    'máy chiếu': 'projector',
    'điều hòa': 'air_conditioner'
}


# =====================================================
# MAIN STAGE HANDLER
# =====================================================

def handle_create_stage(response_text, summary: str, user_input: str, 
                       chain, chat_history, stage_manager) -> Tuple[str, str]:
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
        stage_manager.clear_ticket_data()
        logger.info("User indicated wrong information - clearing data")
        
        response = ("Cảm ơn bạn đã phản hồi. Vui lòng cung cấp lại thông tin "
                   "chính xác để mình tạo ticket mới cho bạn.")
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
    return error_message, "tạo ticket"


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
        normalized['device_type'] = DEVICE_TYPE_MAPPINGS.get(device_type, device_type)
        
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
        
        # Check problem description length
        problem_desc = ticket_data.get('problem_description', '')
        if len(problem_desc) < 10:
            return {
                'valid': False,
                'message': 'Mô tả sự cố quá ngắn. Vui lòng cung cấp mô tả chi tiết hơn (ít nhất 10 ký tự).'
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
        if not isinstance(ticket_data, dict):
            logger.warning("Ticket data is not a dictionary")
            return False, REQUIRED_TICKET_FIELDS.copy()
        
        missing_fields = []
        
        for field in REQUIRED_TICKET_FIELDS:
            value = ticket_data.get(field, '')
            
            # Check if field exists and has meaningful content
            if not value or not str(value).strip():
                missing_fields.append(field)
                continue
            
            # Additional field-specific validation
            is_valid, error_msg = utils.validate_input(str(value), field)
            if not is_valid:
                logger.warning(f"Validation failed for {field}: {error_msg}")
                missing_fields.append(field)
        
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
(Trả lời 'đúng' để xác nhận hoặc 'sai' để nhập lại)"""

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
# HELPER FUNCTIONS
# =====================================================

def extract_ticket_info_from_text(text: str) -> Dict[str, Any]:
    """
    OPTIMIZED: Extract ticket information from free text
    
    Args:
        text: User input text
        
    Returns:
        Dictionary with extracted ticket information
    """
    try:
        ticket_info = {
            'serial_number': '',
            'device_type': '',
            'problem_description': ''
        }
        
        # Simple extraction logic (can be enhanced with NLP)
        words = text.lower().split()
        
        # Look for potential serial numbers (numbers/alphanumeric strings)
        for word in words:
            if len(word) >= 4 and (word.isalnum() or '-' in word or '_' in word):
                if not ticket_info['serial_number']:
                    ticket_info['serial_number'] = word
                    break
        
        # Look for device types
        for device_vn, device_en in DEVICE_TYPE_MAPPINGS.items():
            if device_vn in text.lower():
                ticket_info['device_type'] = device_en
                break
        
        # Use remaining text as problem description
        problem_keywords = ['hỏng', 'lỗi', 'không hoạt động', 'chậm', 'không khởi động']
        for keyword in problem_keywords:
            if keyword in text.lower():
                ticket_info['problem_description'] = f"Thiết bị {keyword}"
                break
        
        logger.debug(f"Extracted ticket info: {ticket_info}")
        return ticket_info
        
    except Exception as e:
        logger.error(f"Error extracting ticket info from text: {e}")
        return {'serial_number': '', 'device_type': '', 'problem_description': ''}


def create_ticket_summary(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    OPTIMIZED: Create a summary of ticket information
    
    Args:
        ticket_data: Ticket data dictionary
        
    Returns:
        Ticket summary dictionary
    """
    try:
        summary = {
            'created_at': datetime.now().isoformat(),
            'serial_number': ticket_data.get('serial_number', ''),
            'device_type': ticket_data.get('device_type', ''),
            'problem_description': ticket_data.get('problem_description', ''),
            'validation_status': 'pending',
            'data_completeness': 'complete' if validate_ticket_data(ticket_data)[0] else 'incomplete'
        }
        
        logger.debug(f"Created ticket summary: {summary}")
        return summary
        
    except Exception as e:
        logger.error(f"Error creating ticket summary: {e}")
        return {}


"""
OPTIMIZATION SUMMARY FOR CREATE.PY:

1. COMPLETE WORKFLOW IMPLEMENTATION:
   - Implemented all missing workflow routes
   - Added comprehensive confirmation handling
   - Enhanced ticket data processing logic
   - Complete integration with stage management

2. ENHANCED VALIDATION:
   - Input validation for all ticket fields
   - Business rule validation
   - Suspicious content detection
   - Data normalization and cleaning

3. ERROR HANDLING IMPROVEMENTS:
   - Try-catch blocks for all major operations
   - Comprehensive logging for debugging
   - Graceful error recovery
   - User-friendly error messages

4. CODE ORGANIZATION:
   - Logical function grouping with clear sections
   - Consistent naming conventions
   - Modular design for easier testing
   - Better separation of concerns

5. INTEGRATION ENHANCEMENTS:
   - Better integration with utils.py functions
   - Enhanced API integration with error handling
   - Improved database interaction logic
   - Better stage management integration

6. USER EXPERIENCE IMPROVEMENTS:
   - Clear confirmation messages
   - Better information formatting
   - Progressive information collection
   - Helpful error guidance
"""