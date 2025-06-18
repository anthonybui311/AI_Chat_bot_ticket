import requests
from dotenv import load_dotenv # type: ignore
import os
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
    api_url = os.getenv("API_FIND_CI_WITH_SN")
    # API Call
    try:
        url = api_url.format(serial_number = serial_number) # type: ignore
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

# API FOR CREATE TICKET
def post_create_ticket(unit, session_id, category, status):
    """
    Create Ticket

    Args:
        dict: Ticket data
            example:
            {
                "unit": "bkk",
                "session_id": "779728226",
                "category": "open-inprogress",
                "status": "all"
            }
    Returns:
        int: Ticket ID
        
    """
    # API URL
    api_url = os.getenv("API_CREATE_TICKET")
    # API Call
    try:
        url = api_url.format(unit = unit, session_id = session_id, category = category, status = status) # type: ignore
        response = requests.post(url)
        if response.status_code == 200:
            ticket_data = response.json()
            return ticket_data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
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
    api_url = os.getenv("API_GET_ALL_TICKET_FOR_SN")
    # API Call
    try:
        url = api_url.format(serial_number = serial_number) # type: ignore
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

def post_update_ticket(unit, session_id, category, status):
    """
    Update Ticket

    Args:
        unit (str): Unit
        session_id (str): Session ID
        category (str): Category
        status (str): Status

    Returns:
        dict: Ticket data
            {
                "ticket_num": "2709636",
                "activity": "update_ticket",
                "response_code": 200,
                "message": "Success"
            }
        
    """
    # API URL
    api_url = os.getenv("API_UPDATE_TICKET")
    # API Call
    try:
        url = api_url.format(unit = unit, session_id = session_id, category = category, status = status) # type: ignore
        response = requests.post(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
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
    api_url = os.getenv("API_GET_TICKET_BY_ID")
    # API Call
    try:
        url = api_url.format(ticket_id = ticket_id) # type: ignore
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
    print("\nUpdate Ticket\n")
    print(post_update_ticket("bkk", "779728226", "open-inprogress", "all"))
    print("\nGet Ticket by ID\n")
    print(get_ticket_by_id("1"))

if __name__ == "__main__":
    main()