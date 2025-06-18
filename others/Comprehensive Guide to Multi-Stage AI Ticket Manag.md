<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Comprehensive Guide to Multi-Stage AI Ticket Management System

## Overview: What We're Building

Hey there! As a senior engineer, I'm excited to walk you through this sophisticated AI-powered ticket management system. Think of it as a smart customer service bot that can create and manage support tickets through natural conversation.

**What makes this special?** Unlike simple chatbots, our system uses a **multi-stage workflow** - it's like having different "rooms" where the AI behaves differently based on what the user is trying to do.

## Architecture Overview

```
User Input → start.py → utils.py → [create.py OR edit.py] → AI Response
                ↓
        Stage Management (MAIN → CREATE → CONFIRMATION → CORRECT)
```


## File-by-File Breakdown

### 1. **config.py** - The Brain's Instructions

Think of this as the "instruction manual" for our AI. It contains different **contexts** (think of them as different personalities) for each stage.

**Key Components:**

#### **CONTEXT** (Main Stage)

```python
CONTEXT = """BẠN LÀ MỘT AI CHATBOT QUẢN LÝ TICKET - NHẬN DIỆN Ý ĐỊNH"""
```

- **Purpose**: Intent recognition - figuring out what the user wants
- **Outputs**: JSON with `response` and `summary` fields
- **Summary Values**: `"tạo ticket"`, `"sửa ticket"`, `"thoát"`, `"không xác định"`


#### **CREATE_CONTEXT** (Create Stage)

```python
CREATE_CONTEXT = """PROMPT TỐI ƯU CHO AI CHATBOT TẠO TICKET"""
```

- **Purpose**: Extract ticket information from user input
- **Outputs**: Either a dictionary with ticket data OR a string response
- **Key Fields**: `serial_number`, `device_type`, `problem_description`


#### **CONFIRMATION_CONTEXT** (Confirmation Stage)

```python
CONFIRMATION_CONTEXT = """PROMPT TỐI ƯU CHO AI CHATBOT XÁC NHẬN TICKET"""
```

- **Purpose**: Sentiment analysis to determine if user confirms or rejects
- **Outputs**: `"đúng"` (correct), `"sai"` (wrong), or other actions
- **Special Feature**: Advanced sentiment analysis


#### **CORRECT_CONTEXT** (Processing Stage)

```python
CORRECT_CONTEXT = """PROMPT TỐI ƯU CHO AI CHATBOT XỬ LÝ TICKET"""
```

- **Purpose**: Handle final ticket processing
- **Outputs**: Processing status and completion messages

**Why separate contexts?** Each stage needs the AI to behave differently. It's like having different job descriptions for the same person!

### 2. **utils.py** - The Central Nervous System

This is the **orchestrator** - it manages everything and makes decisions about where to route user requests.

#### **StageManager Class**

```python
class StageManager:
    def __init__(self):
        self.current_stage = "main"
        self.stage_contexts = {...}
        self.pending_ticket_data = None
```

**What it does:**

- **Tracks current stage**: Knows if we're in MAIN, CREATE, CONFIRMATION, or CORRECT
- **Manages contexts**: Provides the right AI instructions for each stage
- **Stores ticket data**: Remembers ticket information between stages


#### **ChatHistory Class**

```python
class ChatHistory:
    def __init__(self):
        self.messages = []
        self.session_filename = self._create_session_filename()
```

**What it does:**

- **Saves conversations**: Every chat gets saved to a unique file
- **Provides memory**: AI can remember previous messages in the conversation
- **Automatic logging**: No manual file management needed


#### **Core Functions**

**`get_response()`** - The AI Communication Hub

```python
def get_response(chain, chat_history, question, context=""):
    # Sends user input + context to AI
    # Returns (response_data, summary)
```

**`route_to_stage()`** - The Traffic Controller

```python
def route_to_stage(stage_manager, response_text, summary, user_input, chain, chat_history):
    # Decides which stage should handle the request
    # Routes to appropriate handler (create.py or edit.py)
```

**Stage-Specific Handlers:**

- **`handle_confirmation_stage()`**: Processes user confirmations
- **`handle_correct_stage()`**: Manages final ticket processing


### 3. **start.py** - The Main Loop

This is your **application entry point** - the main loop that keeps everything running.

#### **Key Workflow:**

```python
def start():
    # 1. Initialize everything
    chain = utils.create_chain()
    chat_history = utils.ChatHistory()
    stage_manager = utils.StageManager()
    
    # 2. Main conversation loop
    while True:
        user_input = input(f"[{stage_manager.current_stage.upper()}] Bạn: ")
        
        # 3. Get AI response with current context
        response_text, summary = utils.get_response(...)
        
        # 4. Route to appropriate stage
        final_response, final_summary = utils.route_to_stage(...)
        
        # 5. Handle special cases and display response
```

**Special Handling:**

- **Exit conditions**: Recognizes when user wants to quit
- **Stage transitions**: Manages moving between different stages
- **Ticket completion**: Special handling when tickets are created successfully


### 4. **create.py** - The Ticket Factory

This module handles all **ticket creation logic**. It's called when the system is in CREATE stage.

#### **Main Handler Function:**

```python
def handle_create_stage(response_text, summary, user_input, chain, chat_history):
    # Routes based on response type:
    # - Dictionary → process_ticket_data()
    # - String → process_string_response()
```


#### **Key Functions:**

**`process_ticket_data()`** - The Validator

```python
def process_ticket_data(ticket_data, user_input, chain, chat_history):
    is_complete, missing_fields = validate_ticket_data(ticket_data)
    if is_complete:
        return format_ticket_confirmation(ticket_data), "awaiting_confirmation_create"
    else:
        return "Missing fields: ...", "tạo ticket"
```

**`validate_ticket_data()`** - The Quality Checker

```python
def validate_ticket_data(ticket_data):
    required_fields = ['serial_number', 'device_type', 'problem_description']
    # Returns (is_complete, missing_fields)
```

**`format_ticket_confirmation()`** - The Formatter

```python
def format_ticket_confirmation(ticket_data):
    return """Mình xin xác nhận thông tin như sau:
    • S/N hoặc ID thiết bị: {serial_number}
    • Loại thiết bị: {device_type}
    • Nội dung sự cố: {problem_description}
    
    Thông tin này có chính xác không ạ?"""
```


## The Complete Workflow Journey

Let me walk you through a **complete user journey**:

### **Stage 1: MAIN - Intent Recognition**

```
User: "Tôi muốn tạo ticket"
AI Context: CONTEXT (intent recognition)
AI Response: "Tôi sẽ giúp bạn tạo ticket mới..."
Summary: "tạo ticket"
Action: Switch to CREATE stage
```


### **Stage 2: CREATE - Information Gathering**

```
User: "123456, máy in Canon bị kẹt giấy"
AI Context: CREATE_CONTEXT (extract ticket info)
AI Response: {
    "serial_number": "123456",
    "device_type": "máy in Canon", 
    "problem_description": "bị kẹt giấy"
}
Action: Validate → Format confirmation → Switch to CONFIRMATION stage
```


### **Stage 3: CONFIRMATION - User Verification**

```
System: "Mình xin xác nhận thông tin như sau: ..."
User: "Đúng rồi"
AI Context: CONFIRMATION_CONTEXT (sentiment analysis)
AI Response: "Cảm ơn bạn đã xác nhận..."
Summary: "đúng"
Action: Store ticket data → Switch to CORRECT stage
```


### **Stage 4: CORRECT - Final Processing**

```
AI Context: CORRECT_CONTEXT (processing)
AI Response: "Cảm ơn bạn đã xác nhận. Chờ chút để chúng tôi xử lý..."
Summary: "đang xử lý"
Action: Save to database → Generate ticket ID → Complete
Final: "Ticket TK20250617121630 đã được tạo thành công!"
```


## Key Design Patterns \& Best Practices

### **1. State Management Pattern**

```python
class StageManager:
    def switch_stage(self, new_stage):
        if new_stage in self.stage_contexts:
            old_stage = self.current_stage
            self.current_stage = new_stage
            print(f"[STAGE] {old_stage} → {new_stage}")
```

**Why?** Clean separation of concerns - each stage has specific responsibilities.

### **2. Context-Driven AI Behavior**

```python
current_context = stage_manager.get_current_context()
response_text, summary = utils.get_response(..., context=current_context)
```

**Why?** Same AI model, different behaviors based on context. Very powerful!

### **3. Data Flow Management**

```python
# Store data between stages
stage_manager.store_ticket_data(ticket_data)
# Retrieve when needed
ticket_data = stage_manager.get_stored_ticket_data()
```

**Why?** Maintains state across multiple AI interactions.

### **4. Error Handling \& Fallbacks**

```python
try:
    # Main logic
except Exception as e:
    print(f"[ERROR] Create stage: {e}")
    return error_response, "system_error"
```

**Why?** Graceful degradation when things go wrong.

## Advanced Features Explained

### **1. Sentiment Analysis in CONFIRMATION**

The CONFIRMATION_CONTEXT uses advanced sentiment analysis:

```
"đúng rồi, thông tin chính xác" → TÍCH CỰC → "đúng"
"sai rồi, không phải vậy" → TIÊU CỰC → "sai"
```


### **2. Dynamic Context Switching**

```python
def route_to_stage(stage_manager, response_text, summary, ...):
    if stage_manager.current_stage == 'create':
        if final_summary == "awaiting_confirmation_create":
            stage_manager.switch_stage('confirmation')
```


### **3. Persistent Chat History**

```python
def _append_message_to_file(self, sender, message):
    with open(file_path, "a", encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%H:%M:%S')
        f.write(f"[{timestamp}] {sender}: {message}\n\n")
```


## Common Pitfalls for Beginners

### **1. Context Confusion**

❌ **Wrong**: Using same context for all stages
✅ **Right**: Different context for each stage's specific purpose

### **2. State Management**

❌ **Wrong**: Losing data between AI calls
✅ **Right**: Using StageManager to persist data

### **3. Error Handling**

❌ **Wrong**: Letting exceptions crash the system
✅ **Right**: Comprehensive try-catch with fallbacks

### **4. JSON Parsing**

❌ **Wrong**: Assuming AI always returns valid JSON
✅ **Right**: Proper JSON validation and error handling

## Testing Your Understanding

Try to answer these questions:

1. **What happens when a user says "tạo ticket" in MAIN stage?**
2. **How does the system know to move from CREATE to CONFIRMATION stage?**
3. **Where is ticket data stored between stages?**
4. **What makes the AI behave differently in each stage?**

## Extending the System

Want to add a new stage? Here's how:

1. **Add new context** in config.py
2. **Update StageManager** stage_contexts dictionary
3. **Create handler function** in utils.py
4. **Add routing logic** in route_to_stage()
5. **Test the new workflow**

## Performance Considerations

- **Memory**: Chat history grows over time
- **AI Calls**: Each user input triggers an AI request
- **File I/O**: Every message gets written to disk
- **Error Recovery**: System should handle AI failures gracefully

This system demonstrates **enterprise-level architecture** with proper separation of concerns, state management, and error handling. It's a great example of how to build scalable, maintainable AI applications!

The beauty is in how all four files work together - each has a specific job, but they communicate seamlessly to create a smooth user experience. That's the mark of good software architecture!

<div style="text-align: center">⁂</div>

[^1]: config.py

[^2]: utils.py

[^3]: start.py

[^4]: create.py

[^5]: https://www.chatbees.ai/blog/ticketing-system-workflow

[^6]: https://gcore.com/learning/what-is-an-ai-chatbot

[^7]: https://www.gptbots.ai/blog/ticket-automation

[^8]: https://www.creolestudios.com/beginners-guide-to-ai-chatbot-development/

[^9]: https://irisagent.com/blog/ai-powered-ticket-automation-complete-guide-on-meaning-pros-and-steps/

[^10]: https://www.zendesk.com/sg/blog/ai-powered-ticketing/

[^11]: https://www.atomicwork.com/it-service-desk/ai-ticketing-system-guide

[^12]: https://www.youtube.com/watch?v=N-HorjMlmco

[^13]: https://www.thebricks.com/resources/guide-how-to-create-a-ticketing-system-in-excel-using-ai

[^14]: https://www.deskdirector.com/dd-blog/ai-ticketing-system

