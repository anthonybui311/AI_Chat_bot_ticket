# AI Chat Bot Ticket System

An intelligent chatbot system for managing and handling support tickets using Groq's LLM.

## Overview
This system provides an AI-powered interface for:
- Creating new support tickets
- Editing existing tickets
- Managing ticket statuses
- Handling ticket updates and modifications

The system consists of:
- FastAPI backend for robust API endpoints and ticket management
- Streamlit frontend for an intuitive user interface
- Groq LLM integration for intelligent responses

## Prerequisites
- Python 3.12 or higher
- Virtual environment management tool (venv)
- Git for version control
- Groq API key for LLM functionality
- FastAPI for backend services
- Streamlit for frontend interface

## Project Structure
```
AI_Chat_bot_ticket/
├── main.py                 # Main application entry point (FastAPI + Streamlit)
├── requirements.txt        # Project dependencies
├── README.md              # Project documentation
├── others/                # Additional resources
└── working/              # Main working directory
    ├── backend/          # Backend logic and API handlers
    │   ├── api_part/     # FastAPI routes and endpoints
    │   │   ├── api_routes.py  # API endpoint definitions
    │   │   └── api_call.py    # API utility functions
    │   ├── utility/      # Utility functions
    │   ├── creating_part/# Ticket creation logic
    │   ├── editing_part/ # Ticket editing logic
    │   └── starting_part/# Initialization logic
    ├── chat_env/         # Virtual environment
    ├── configuration/    # Configuration files
    │   └── config.py     # System configuration
    ├── data/            # Data storage
    ├── frontend/        # Streamlit UI components
    │   ├── app.py       # Main Streamlit application
    │   ├── pages/       # Streamlit pages
    │   │   ├── about_us.py     # About page
    │   │   └── current_chat.py # Chat interface
    │   └── utils/       # Frontend utilities
    │       └── api_client.py   # Backend API client
    └── logs/           # Log files
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd AI_Chat_bot_ticket
   ```

2. **Set Python Path**
   ```bash
   # For macOS/Linux
   export PYTHONPATH="/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket:$PYTHONPATH"
   
   # Add to ~/.zshrc or ~/.bashrc for persistence
   echo 'export PYTHONPATH="/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket:$PYTHONPATH"' >> ~/.zshrc
   ```

3. **Virtual Environment Setup**
   ```bash
   # Create virtual environment if it doesn't exist
   python -m venv working/chat_env
   
   # Activate the virtual environment
   source working/chat_env/bin/activate  # For macOS/Linux
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Key Dependencies:
   - langchain_groq - For LLM integration
   - groq - For API interactions
   - python-dotenv - For environment management
   - fastapi - For backend API
   - uvicorn - For ASGI server
   - streamlit - For frontend interface
   - requests - For API calls

5. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_api_key_here
   LOG_DIRECTORY=/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/logs
   DATA_PATH=/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data
   ```

## Running the Application

1. **Activate Environment**
   ```bash
   source working/chat_env/bin/activate
   ```

2. **Start the Application**
   ```bash
   python main.py
   ```

   This will start:
   - FastAPI backend server (default: http://localhost:8000)
   - Streamlit frontend interface (default: http://localhost:8501)

   You can access:
   - Frontend UI: http://localhost:8501
   - API documentation: http://localhost:8000/docs

## Features

### Frontend (Streamlit)
- Interactive chat interface
- Real-time conversation history
- About page with system information
- Automatic session management
- Support for Vietnamese language
- Exit handling with keywords ("thoát", "tạm biệt", etc.)

### Backend (FastAPI)
- RESTful API endpoints
- Ticket management system
- LLM integration for responses
- Session handling
- Logging and monitoring
- Error handling and validation

## Development Guidelines

### Logging
- Logs are stored in `working/logs/`
- Each session creates a new log file
- Log format: `chatbot_YYYYMMDD_HHMMSS.log`
- To enable terminal logging, uncomment this line in `working/backend/starting_part/start.py`:
  ```python
  # logging.StreamHandler()  # Also log but to terminal
  ```

### Data Storage
- Ticket data stored in `working/data/`
- Chat histories saved as text files
- Session data maintained during runtime

### Configuration
- System settings in `configuration/config.py`
- Environment variables in `.env`
- API configurations in respective modules

## Troubleshooting

### Common Issues
1. **Import Errors**
   - Verify PYTHONPATH is set correctly
   - Ensure virtual environment is activated
   - Check package installations

2. **API Errors**
   - Verify Groq API key is set
   - Check network connectivity
   - Review API call logs

3. **Environment Issues**
   - Confirm Python version (3.12+)
   - Verify virtual environment activation
   - Check dependency conflicts

## Support and Documentation
For additional support:
- Check the logs directory for detailed error messages
- Review the configuration files for proper settings
- Consult the API documentation for integration details

## License
[Your License Here] 