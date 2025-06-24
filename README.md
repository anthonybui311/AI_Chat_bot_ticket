# AI Chat Bot Ticket System
## Setup Guide

### Prerequisites
- Python 3.12 or higher
- Virtual environment management tool (venv)
- Git (for version control)

### Project Structure
```
working/
├── backend/         # Backend logic and API handlers
├── chat_env/        # Virtual environment directory
├── configuration/   # Configuration files
├── data/           # Data storage
├── frontend/       # UI components
├── logs/           # Log files
├── pipeline/       # Processing pipeline
└── main.py         # Main application entry point
```

### Setup Instructions

1. **Set Python Path**
   First, you need to set the Python path to include the working directory. Run this command in your terminal:
   ```bash
   export PYTHONPATH="/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket:$PYTHONPATH"
   ```
   
   For permanent setup, add this line to your `~/.bashrc` or `~/.zshrc` file.

2. **Virtual Environment Setup**
   ```bash
   # Navigate to the project directory
   cd /Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket

   # Activate the existing virtual environment
   source working/chat_env/bin/activate

   # If virtual environment doesn't exist, create it:
   python -m venv working/chat_env
   source working/chat_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Make sure you're in the virtual environment (you should see (chat_env) in your terminal)
   pip install -r requirements.txt
   ```

   Key dependencies include:
   - langchain_groq - For AI/ML functionality
   - groq - Version 0.4.1
   - python-dotenv - Version 1.0.0 for environment management
   - requests - Version 2.32.3 for API calls
   - streamlit - Version 1.35.0 for frontend

4. **Environment Variables**
   Create a `.env` file in the working directory with necessary environment variables (if required).

### Running the Application
1. Ensure your Python path is set correctly
2. Activate the virtual environment
3. Run the main application:
   ```bash
   python working/main.py
   ```

### Troubleshooting
- If you encounter import errors, verify that your PYTHONPATH is set correctly
- For package-related issues, ensure you're in the virtual environment when installing packages
- Check the logs directory for detailed error messages

### Notes
- Always activate the virtual environment before running the application
- Keep the requirements.txt file updated when adding new dependencies
- Monitor the logs directory for debugging information

### Support
For any issues or questions, please refer to the project documentation or contact the development team. 