from dotenv import load_dotenv
load_dotenv()

# Import datetime to create unique filenames with timestamps
from datetime import datetime
import os

# Import the Groq LLM wrapper for LangChain (make sure you have a Groq API key)
from langchain_groq import ChatGroq

# Import prompt-related classes to build structured prompts for the chatbot
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import message types for chat history
from langchain_core.messages import HumanMessage, AIMessage



# --- CHAT HISTORY CLASS ---

class ChatHistory:
    """
    Stores conversation history as a list of messages.
    Each conversation session gets its own unique file.
    """
    def __init__(self):
        # List to store all messages in current conversation
        self.messages = []
        # Create a unique filename for this conversation session
        self.session_filename = self._create_session_filename()
        # Create the file immediately when a new session starts
        self._initialize_session_file()
    
    def _create_session_filename(self):
        """
        Creates a unique filename using current date and time.
        Format: chat_YYYY-MM-DD_HH-MM-SS.txt
        Example: chat_2024-12-15_14-30-25.txt
        """
        # Get current date and time
        now = datetime.now()
        # Format it as a string that's safe for filenames (no colons or spaces)
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Create the filename
        filename = f"chat_{timestamp}.txt"
        return filename
    
    def _initialize_session_file(self):
        """
        Creates the session file and writes a header to mark the start of conversation.
        This runs once when each new ChatHistory object is created.
        """
        # Create the full file path
        file_path = f"/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data/{self.session_filename}"
        
        
        # Create the file and write a header
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(f"=== New Chat Session Started ===\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"=" * 40 + "\n\n")
        
        print(f"New conversation session started. Saving to: {self.session_filename}")
    
    def add_user_message(self, message):
        """
        Add a user message to history and immediately save it to file.
        This ensures we don't lose messages if the program crashes.
        """
        # Add message to our internal list
        self.messages.append(HumanMessage(content=message))
        # Immediately write this message to the file
        self._append_message_to_file("User", message)
    
    def add_ai_message(self, message):
        """
        Add an AI message to history and immediately save it to file.
        This ensures we don't lose messages if the program crashes.
        """
        # Add message to our internal list
        self.messages.append(AIMessage(content=message))
        # Immediately write this message to the file
        self._append_message_to_file("AI", message)
    
    def _append_message_to_file(self, sender, message):
        """
        Append a single message to the session file.
        
        Args:
            sender: Either "User" or "AI" 
            message: The actual message content
        """
        # Create the full file path
        file_path = f"/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data/{self.session_filename}"
        
        # Append the message to the file (don't overwrite, just add to the end)
        with open(file_path, "a", encoding='utf-8') as f:
            # Write timestamp and message
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] {sender}: {message}\n\n")
    
    def get_messages(self):
        """Get all messages in history (needed for the AI to remember conversation)"""
        return self.messages
    
    def clear(self):
        """
        Clear chat history and start a new session file.
        This creates a completely new conversation session.
        """
        # Clear the messages from memory
        self.messages = []
        # Create a new filename for the new session
        self.session_filename = self._create_session_filename()
        # Initialize the new session file
        self._initialize_session_file()


# --- PROMPT TEMPLATE FUNCTION ---

def create_chat_prompt():
    """
    Creates a chat prompt template using the modern LangChain approach.
    - Uses MessagesPlaceholder for chat history
    - Includes system message and human input
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant. Use the following context to answer questions:
Context: {context}

Please provide helpful and accurate responses based on the context and conversation history."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    return prompt


# --- LLM FUNCTION ---

def create_llm():
    """
    Initializes the Groq Llama 3 model as the chatbot's brain.
    - model_name: Choose the Llama 3 variant you want (check Groq docs for available models).
    - temperature: Controls randomness (0 = deterministic, 1 = very creative).
    """
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",  
        temperature=0.7
    )
    return llm


# --- CHAIN FUNCTION ---

def create_chain():
    """
    Assembles the chatbot pipeline using modern LangChain patterns:
    - Uses RunnableSequence (prompt | llm) instead of deprecated LLMChain
    - Integrates with our custom chat history manager
    """
    prompt = create_chat_prompt()
    llm = create_llm()
    
    # Modern LangChain chaining approach
    chain = prompt | llm
    
    return chain


# --- CHAT FUNCTION ---

def get_response(chain, chat_history, question, context=""):
    """
    Get a response from the chatbot chain.
    
    Args:
        chain: The LangChain runnable chain
        chat_history: ChatHistory instance
        question: User's question
        context: Additional context (optional)
    
    Returns:
        AI response as string
    """
    # Prepare input for the chain
    chain_input = {
        "question": question,
        "context": context,
        "chat_history": chat_history.get_messages()
    }
    
    # Get response from chain
    response = chain.invoke(chain_input)
    
    # Extract content from AIMessage
    if hasattr(response, 'content'):
        return response.content
    else:
        return str(response)


# --- MAIN CHAT LOOP ---

def main():
    """
    Runs the chatbot in a command-line loop.
    Each time this function runs, it creates a NEW conversation session.
    - Prompts the user for input.
    - Calls the chatbot chain to get a response.
    - Prints the AI's reply.
    - Maintains chat history and saves everything to a unique file.
    - Exits when the user types 'exit', 'quit', or 'bye'.
    """
    print("Chatbot initialized. Type 'exit' or 'quit' or 'bye' to end conversation.")
    print("Type 'clear' to clear chat history and start a new session file.")
    print("Type 'new' to start a completely new conversation session.")
    
    # Initialize chain and chat history
    # IMPORTANT: This creates a NEW session file each time main() is called
    chain = create_chain()
    chat_history = ChatHistory()  # This automatically creates a new session file

    # This loop keeps the chatbot running until the user wants to stop.
    while True:
        user_input = input("\nYou: ")

        # Check if user wants to exit the program completely
        if user_input.lower() in ['exit', 'quit', 'bye']:
            # Write a session end marker to the file
            file_path = f"/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data/{chat_history.session_filename}"
            with open(file_path, "a", encoding='utf-8') as f:
                f.write(f"\n=== Session Ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            
            print("Chatbot: Goodbye!")
            print(f"Conversation saved to: {chat_history.session_filename}")
            break
        
        # Check if user wants to clear history (start new session in same file)
        if user_input.lower() == 'clear':
            chat_history.clear()  # This creates a new session file
            print("Chatbot: Chat history cleared! New session started.")
            continue
        
        # Check if user wants to start completely new conversation
        if user_input.lower() == 'new':
            # End current session
            file_path = f"/Users/vietbui/Desktop/Projects/AI_Chat_bot_ticket/working/data/{chat_history.session_filename}"
            with open(file_path, "a", encoding='utf-8') as f:
                f.write(f"\n=== Session Ended - New Session Requested at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            
            print(f"Previous conversation saved to: {chat_history.session_filename}")
            
            # Start completely new session
            chat_history = ChatHistory()  # Creates brand new session file
            print("Chatbot: New conversation started!")
            continue

        try:
            # Get response from the chain
            response_text = get_response(
                chain=chain,
                chat_history=chat_history,
                question=user_input,
                context=""  # You can add context here if needed
            )
            
            # Add messages to history (this automatically saves them to file)
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(response_text)
            
            print(f"Chatbot: {response_text}")
            
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")


# --- SCRIPT ENTRY POINT ---

if __name__ == "__main__":
    # Each time you run this script, it will create a NEW conversation session
    # If you want to have multiple separate conversations, you can:
    # 1. Run the script multiple times (each creates new session)
    # 2. Use the 'new' command during conversation
    # 3. Use the 'clear' command to reset current session
    main()