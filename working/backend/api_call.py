import requests
from dotenv import load_dotenv # type: ignore
from typing import Optional, Dict, Any
import os
import json
load_dotenv()
# APIs FOR CREATE TICKET


# API FOR GET CI WITH SERIAL NUMBER
def get_ci_with_sn(serial_number):
    """
    Get CI with Serial Number

    Args:
        serial_number (str): Serial Number

    Returns:
        list: List of CI data
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
    # API URL
    api_base_url = os.getenv("API_FIND_CI_WITH_SN")
    if not api_base_url:
        print("Error: API_CREATE_TICKET environment variable not set")
        return None
    # API Call
    try:
        url = api_base_url.format(serial_number = serial_number) # type: ignore
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json() #print json content in dictionary format
            return data
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def post_create_ticket(unit: str, session_id: str, category: str, status: str) -> Optional[Dict[Any, Any]]:
    """
    Create Ticket via API
    
    Args:
        unit (str): Unit identifier (e.g., "bkk")
        session_id (str): Session ID (e.g., "779728226")
        category (str): Ticket category (e.g., "open-inprogress")
        status (str): Ticket status (e.g., "all")
        
    Returns:
        Optional[Dict[Any, Any]]: Ticket data if successful, None if failed
        
    Example:
        >>> result = post_create_ticket("bkk", "779728226", "open-inprogress", "all")
        >>> print(result)
    """
    # Get API URL from environment variable
    api_base_url = os.getenv("API_CREATE_TICKET")
    
    if not api_base_url:
        print("Error: API_CREATE_TICKET environment variable not set")
        return None
    
    try:
        # Construct the full URL with query parameters
        url = f"{api_base_url}?unit={unit}&sessionid={session_id}&Category={category}&status={status}"
        
        # Make the API call
        response = requests.post(url, timeout=15)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                ticket_data = response.json()
                print(f"API: {response.status_code} - {response.text}")
                return ticket_data
            except ValueError as json_error:
                print(f"Error parsing JSON response: {json_error}")
                return None
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None

    
def get_all_ticket_for_sn(serial_number):
    """
    Get All Ticket for Serial Number

    Args:
        serial_number (str): Serial Number

    Returns:
        list: List of Ticket data
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
    # API URL
    api_base_url = os.getenv("API_GET_ALL_TICKET_FOR_SN")
    
    if not api_base_url:
        print("Error: API_CREATE_TICKET environment variable not set")
        return None
    # API Call
    try:
        url = api_base_url.format(serial_number = serial_number) # type: ignore
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    
# APIs FOR EDIT TICKET

def post_update_ticket(unit: str, session_id: str, category: str, status: str) -> Optional[Dict[Any, Any]]:
    """
    Update Ticket via API
    
    Args:
        unit (str): Unit identifier (e.g., "bkk")
        session_id (str): Session ID (e.g., "779728226")
        category (str): Ticket category (e.g., "open-inprogress")
        status (str): Ticket status (e.g., "all")
        
    Returns:
        Optional[Dict[Any, Any]]: Ticket data if successful, None if failed
        
        Success response example:
        {
            "ticket_num": "2709636",
            "activity": "update_ticket",
            "response_code": 200,
            "message": "Success"
        }
        
    Example:
        >>> result = post_update_ticket("bkk", "779728226", "open-inprogress", "all")
        >>> if result:
        ...     print(f"Ticket {result['ticket_num']} updated successfully")
    """
    # Get API URL from environment variable
    api_base_url = os.getenv("API_UPDATE_TICKET")
    
    if not api_base_url:
        print("Error: API_UPDATE_TICKET environment variable not set")
        return None
    
    try:
        # Construct the full URL with query parameters
        url = f"{api_base_url}?unit={unit}&sessionid={session_id}&Category={category}&status={status}"
        
        # Make the API call
        response = requests.post(url, timeout=30)
        
        # Check if request was successful
        if response.status_code == 200:
            try:
                ticket_data = response.json()
                return ticket_data
            except ValueError as json_error:
                print(f"Error parsing JSON response: {json_error}")
                return None
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return None


def get_ticket_by_id(ticket_id):
    """
    Get Ticket by ID

    Args:
        ticket_id (str): Ticket ID

    Returns:
        list: List of Ticket data
            [
                {
                    "ticketid": "2709798",
                    "assignee": "ahd",
                    "status": "Open",
                    "summary": "Summary Service Desk Incident None"
                }
            ]
        
    """
    # API URL
    api_base_url = os.getenv("API_GET_TICKET_BY_ID")
    if not api_base_url:
        print("Error: API_CREATE_TICKET environment variable not set")
        return None
    # API Call
    try:
        url = api_base_url.format(ticket_id = ticket_id) # type: ignore
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
def main():
    print("Get CI with Serial Number\n")
    print(get_ci_with_sn("48917912"))
    print("\nCreate Ticket\n")
    print(post_create_ticket("bkk", "779728226", "open-inprogress", "all"))
    print("\nGet All Ticket for Serial Number\n")
    print(get_all_ticket_for_sn("37926762"))
    # [{'ticketid': '2709474', 'assignee': 'bk_smmobile', 
    # 'status': 'In Progress', 'summary': 'test ký bb 3'}, 
    #  {'ticketid': '2678474', 'assignee': 'dinhcnm', 
    #   'status': 'Open', 'summary': 'BDDK CK 02 ( 27/03 - 27/05/2021 )'}]
    
    print("\nUpdate Ticket\n")
    print(post_update_ticket("bkk", "779728226", "open-inprogress", "all"))
    print("\nGet Ticket by ID\n")
    print(get_ticket_by_id("1"))

if __name__ == "__main__":
    main()