import requests
import logging
import time
from dotenv import load_dotenv 
from typing import Optional, Dict, Any, List 
import os

# Load environment variables
load_dotenv()

# Configure module logger
logger = logging.getLogger(__name__)


# =====================================================
# CONFIGURATION AND CONSTANTS
# =====================================================

# API Configuration
DEFAULT_TIMEOUT = 15  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds between retries

# Response status codes
STATUS_SUCCESS = 200
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500

# API Endpoints (from environment variables)
API_ENDPOINTS = {
    'find_ci': os.getenv("API_FIND_CI_WITH_SN"),
    'create_ticket': os.getenv("API_CREATE_TICKET"),
    'get_tickets_by_sn': os.getenv("API_GET_ALL_TICKET_FOR_SN"),
    'update_ticket': os.getenv("API_UPDATE_TICKET"),
    'get_ticket_by_id': os.getenv("API_GET_TICKET_BY_ID")
}


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def validate_api_config() -> Dict[str, Any]:
    """
    OPTIMIZED: Validate API configuration
    
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'valid': True,
        'missing_endpoints': [],
        'warnings': []
    }
    
    for endpoint_name, endpoint_url in API_ENDPOINTS.items():
        if not endpoint_url:
            validation_result['missing_endpoints'].append(endpoint_name)
            validation_result['valid'] = False
    
    if validation_result['missing_endpoints']:
        logger.error(f"Missing API endpoints: {validation_result['missing_endpoints']}")
    
    return validation_result


def make_api_request(url: str, method: str = 'GET', json: Optional[Dict] = None, 
                    timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_RETRY_ATTEMPTS) -> Optional[Dict[str, Any]]:
    """
    OPTIMIZED: Make API request with comprehensive error handling and retry logic
    
    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request payload for POST/PUT requests
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        
    Returns:
        Response data as dictionary or None if failed
    """
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"API Request (attempt {attempt + 1}): {method}")
            
            if method.upper() == 'GET':
                response = requests.get(url, json=json, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=json, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=json, timeout=timeout)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            # Check response status
            if response.status_code == STATUS_SUCCESS:
                result = response.json()
                logger.info(f"API Success: {response.status_code}")
                return result

                    
            elif response.status_code == STATUS_NOT_FOUND:
                logger.warning(f"API Not Found: {response.status_code}")
                return None
                
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                if attempt < max_retries:
                    time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                    continue
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {timeout} seconds (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e} (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    logger.error(f"All retry attempts failed for {method} {url}")
    return None


def validate_response_data(data: Any, expected_fields: List[str] = None) -> Dict[str, Any]: #type: ignore
    """
    OPTIMIZED: Validate API response data
    
    Args:
        data: Response data to validate
        expected_fields: List of expected fields in response
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if data is None:
        result['valid'] = False
        result['errors'].append("Response data is None")
        return result
    
    if not isinstance(data, (dict, list)):
        result['warnings'].append(f"Unexpected response type: {type(data)}")
    
    if expected_fields and isinstance(data, dict):
        for field in expected_fields:
            if field not in data:
                result['warnings'].append(f"Missing expected field: {field}")
    
    return result


# =====================================================
# CI (CONFIGURATION ITEM) OPERATIONS
# =====================================================

def get_ci_with_sn(serial_number: str) -> Optional[List[Dict[str, Any]]]:
    """
    OPTIMIZED: Get Configuration Item(s) by Serial Number
    
    Args:
        serial_number: Device serial number
        
    Returns:
        List of CI data or None if not found
        
    Example Response:
    [
        {
            "CI_Id": "80000314",
            "Name": "ATM_48917912",
            "SerialNum": "48917912",
            "Type": null,
            "Location": "Nhà máy M1 An Khánh, Hoài Đức, Hà Nội",
            "State": null,
            "Province": null,
            "Zone": null,
            "Status": null,
            "Contract_Id": null,
            "Contract_Name": "HD032017-03-MB"
        }
    ]
    """
    try:
        if not serial_number or not serial_number.strip():
            logger.error("Serial number is required")
            return None
        
        api_url = API_ENDPOINTS['find_ci']
        if not api_url:
            logger.error("API endpoint for find_ci not configured")
            return None
        
        # Format URL with serial number
        url = api_url.format(serial_number=serial_number.strip())
        
        logger.info(f"Getting CI data for serial number: {serial_number}")
        
        response_data = make_api_request(url, method='GET')
        
        if response_data is None:
            logger.info(f"No CI data found for serial number: {serial_number}")
            return None
        
        # Validate response
        validation = validate_response_data(response_data)
        if not validation['valid']:
            logger.warning(f"CI response validation issues: {validation['errors']}")
        
        # Ensure response is always a list
        if isinstance(response_data, dict):
            ci_list = [response_data]
        elif isinstance(response_data, list):
            ci_list = response_data
        else:
            logger.warning(f"Unexpected CI response format: {type(response_data)}")
            return None
        
        logger.info(f"Found {len(ci_list)} CI record(s) for serial: {serial_number}")
        return ci_list
        
    except Exception as e:
        logger.error(f"Error getting CI data for {serial_number}: {e}")
        return None


# =====================================================
# TICKET CREATION OPERATIONS
# =====================================================

def post_create_ticket(serial_number: str, summary: str) -> Optional[str]:
    """
    OPTIMIZED: Create ticket via API with enhanced error handling
    """
    try:
        api_url = API_ENDPOINTS['create_ticket']
        if not api_url:
            logger.error("API endpoint for create_ticket not configured")
            return None
        
        payload = {
                "serialnum": serial_number,
                "sessionid": "1111",
                "summary": summary,
                "requested":"nganpt",
                "Area":"lỗi sự cố",
                "affectedEndUser": "HD032017-03-MB"
            }
        
        # Construct URL with query parameters
        
        logger.info(f"API URL: {api_url}")
        
        logger.info(f"Creating ticket - Serial Number: {serial_number}, Summary: {summary}")
        
        response_data = make_api_request(api_url, method='POST', json=payload)
        
        if response_data is None:
            logger.error("Failed to create ticket - no response data")
            return None

        # Handle case where response_data is an integer
        if isinstance(response_data, int):
            logger.info(f"Received ticket ID as integer: {response_data}")
            return str(response_data)
            
        # Handle dictionary response
        if isinstance(response_data, dict):
            # Validate response structure
            expected_fields = ['ticket_num', 'response_code', 'message']
            validation = validate_response_data(response_data, expected_fields)
            
            # Extract ticket ID
            ticket_id = response_data.get('ticket_num') or response_data.get('ticketid')
            response_code = response_data.get('response_code', 0)
            message = response_data.get('message', 'Unknown')
            
            if response_code == STATUS_SUCCESS and ticket_id:
                logger.info(f"Ticket created successfully: {ticket_id}")
                return str(ticket_id)
            else:
                logger.error(f"Ticket creation failed: Code {response_code}, Message: {message}")
                return None
        
        logger.error(f"Unexpected response type: {type(response_data)}")
        return None
            
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return None


def validate_ticket_creation_params(unit: str, session_id: str, category: str, status: str) -> Dict[str, Any]:
    """
    OPTIMIZED: Validate ticket creation parameters
    
    Args:
        unit: Unit identifier
        session_id: Session ID
        category: Ticket category
        status: Ticket status
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': []
    }
    
    # Validate unit
    if not unit or len(unit) < 2:
        result['errors'].append("Unit must be at least 2 characters")
    
    # Validate session_id (should be numeric)
    if not session_id or not session_id.isdigit():
        result['errors'].append("Session ID must be numeric")
    
    # Validate category
    valid_categories = ['open-inprogress', 'resolved', 'closed']
    if category not in valid_categories:
        result['errors'].append(f"Category must be one of: {valid_categories}")
    
    # Validate status
    valid_statuses = ['all', 'open', 'closed', 'pending']
    if status not in valid_statuses:
        result['errors'].append(f"Status must be one of: {valid_statuses}")
    
    result['valid'] = len(result['errors']) == 0
    return result


# =====================================================
# TICKET RETRIEVAL OPERATIONS
# =====================================================

def get_all_ticket_for_sn(serial_number: str) -> Optional[List[Dict[str, Any]]]:
    """
    OPTIMIZED: Get all tickets for a specific serial number
    
    Args:
        serial_number: Device serial number
        
    Returns:
        List of ticket data or None if not found
        
    Example Response:
    [
        {
            "ticketid": "2709474",
            "assignee": "bk_smmobile",
            "status": "In Progress",
            "summary": "test ký bb 3"
        },
        {
            "ticketid": "2678474",
            "assignee": "dinhcnm",
            "status": "Open",
            "summary": "BDDK CK 02 ( 27/03 - 27/05/2021 )"
        }
    ]
    """
    try:
        if not serial_number or not serial_number.strip():
            logger.error("Serial number is required")
            return None
        
        api_url = API_ENDPOINTS['get_tickets_by_sn']
        if not api_url:
            logger.error("API endpoint for get_tickets_by_sn not configured")
            return None
        
        # Format URL with serial number
        url = api_url.format(serial_number=serial_number.strip())
        
        logger.info(f"Getting tickets for serial number: {serial_number}")
        
        response_data = make_api_request(url, method='GET')
        
        if response_data is None:
            logger.info(f"No tickets found for serial number: {serial_number}")
            return None
        
        # Validate response
        validation = validate_response_data(response_data)
        if not validation['valid']:
            logger.warning(f"Ticket response validation issues: {validation['errors']}")
        
        # Ensure response is always a list
        if isinstance(response_data, dict):
            ticket_list = [response_data]
        elif isinstance(response_data, list):
            ticket_list = response_data
        else:
            logger.warning(f"Unexpected ticket response format: {type(response_data)}")
            return None
        
        logger.info(f"Found {len(ticket_list)} ticket(s) for serial: {serial_number}")
        return ticket_list
        
    except Exception as e:
        logger.error(f"Error getting tickets for {serial_number}: {e}")
        return None


def get_ticket_by_id(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    OPTIMIZED: Get ticket by specific ticket ID
    
    Args:
        ticket_id: Ticket ID to retrieve
        
    Returns:
        Ticket data or None if not found
        
    Example Response:
    {
        "ticketid": "2709798",
        "assignee": "ahd",
        "status": "Open",
        "summary": "Summary Service Desk Incident None",
        "created_date": "2023-01-15",
        "priority": "Medium"
    }
    """
    try:
        if not ticket_id or not ticket_id.strip():
            logger.error("Ticket ID is required")
            return None
        
        api_url = API_ENDPOINTS['get_ticket_by_id']
        if not api_url:
            logger.error("API endpoint for get_ticket_by_id not configured")
            return None
        
        # Format URL with ticket ID
        url = api_url.format(ticket_id=ticket_id.strip())
        
        logger.info(f"Getting ticket by ID: {ticket_id}")
        
        response_data = make_api_request(url, method='GET')
        
        if response_data is None:
            logger.info(f"Ticket not found: {ticket_id}")
            return None
        
        # Validate response
        expected_fields = ['ticketid', 'status']
        validation = validate_response_data(response_data, expected_fields)
        if not validation['valid']:
            logger.warning(f"Ticket response validation issues: {validation['errors']}")
        
        # Handle both single ticket and list responses
        if isinstance(response_data, list):
            if len(response_data) > 0:
                ticket_data = response_data[0] #type: ignore
            else:
                logger.info(f"Empty ticket list for ID: {ticket_id}")
                return None
        else:
            ticket_data = response_data
        
        logger.info(f"Retrieved ticket: {ticket_id}")
        return ticket_data
        
    except Exception as e:
        logger.error(f"Error getting ticket {ticket_id}: {e}")
        return None


# =====================================================
# TICKET UPDATE OPERATIONS
# =====================================================
# api_call.py - Enhanced API Update Handling

def post_update_ticket(ticket_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    OPTIMIZED: Update ticket via API with full validation and error handling
    """
    try:
        if not ticket_id or not ticket_id.strip():
            logger.error("Ticket ID is required for update")
            return None

        if not update_data:
            logger.error("Update data is required")
            return None

        api_url = API_ENDPOINTS['update_ticket']
        if not api_url:
            logger.error("API endpoint for update_ticket not configured")
            return None

        # Prepare update payload - only include keys that exist in update_data
        payload = {"ticket_num": ticket_id}
        
        # Map update_data keys to API payload keys
        field_mapping = {
            'summary': 'ticket_summary',
            'status': 'status',
            'session_id': 'sessionid'
        }
        
        # Only add fields that exist in update_data
        for update_key, api_key in field_mapping.items():
            if update_key in update_data:
                payload[api_key] = update_data[update_key]

        logger.info(f"Updating ticket {ticket_id} with data: {update_data}")
        logger.info(f"API payload: {payload}")
        
        response_data = make_api_request(api_url, method='POST', json=payload)

        if response_data and response_data.get('response_code') == STATUS_SUCCESS:
            logger.info(f"Ticket {ticket_id} updated successfully")
            return response_data
        else:
            logger.error(f"Failed to update ticket {ticket_id}: {response_data}")
            return None

    except Exception as e:
        logger.error(f"Error updating ticket {ticket_id}: {e}")
        return None


# =====================================================
# MAIN FUNCTION FOR TESTING
# =====================================================

def main():
    """
    OPTIMIZED: Main function for testing API operations
    """
    print("=== API CALL MODULE TESTING ===")
    
    # Validate configuration
    config_validation = validate_api_config()
    print(f"Configuration validation: {config_validation}")
    
    if not config_validation['valid']:
        print("❌ API configuration invalid. Please check environment variables.")
        return
    
    # Test CI data retrieval
    print("\n1. Testing CI data retrieval...")
    ci_data = get_ci_with_sn("48917912")
    print(f"CI Data: {ci_data}")
    
    # Test ticket creation
    print("\n2. Testing ticket creation...")
    ticket_id = post_create_ticket("48917912", "máy in hết mực")
    print(f"Created Ticket ID: {ticket_id}")
    
    # Test ticket retrieval
    print("\n3. Testing ticket retrieval...")
    tickets = get_all_ticket_for_sn("37926762")
    print(f"Tickets for SN: {tickets}")
    
    # Test specific ticket lookup
    print("\n4. Testing ticket lookup by ID...")
    ticket = get_ticket_by_id("2709798")
    print(f"Ticket by ID: {ticket}")
    
    print("\n5. Testing ticket update...")
    update_data = {
        "ticket_num": "2709798",
        "summary": "máy in hết mực",
        "session_id": "1111"
    }
    updated_ticket = post_update_ticket(update_data['ticket_num'], update_data)
    print(f"Updated Ticket: {updated_ticket}")


if __name__ == "__main__":
    main()