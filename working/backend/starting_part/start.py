# start.py

"""
File chính chịu trách nhiệm:
- Lấy input từ người dùng ở giai đoạn đầu
- Điều hướng đến các module xử lý tương ứng
- Duy trì lịch sử hội thoại liên tục
"""

import backend.editing_part.edit as edit
import backend.creating_part.create as create
import backend.utils as utils
import configuration.config as config


# --- MAIN FUNCTION ---
def start():
    """
    Hàm chính điều khiển toàn bộ luồng chatbot:
    - Khởi tạo chain và chat history
    - Chạy vòng lặp chính để lấy input từ người dùng
    - Phân tích ý định NGAY LẬP TỨC và điều hướng đến module tương ứng
    - Duy trì lịch sử hội thoại liên tục
    """
    print("Chatbot được khởi động. Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện.")
    
    # Khởi tạo chain và chat history - TẠO SESSION MỚI
    chain = utils.create_chain()
    chat_history = utils.ChatHistory()
    
    # Context cho AI để hiểu nhiệm vụ
    context = config.CONTEXT
    
    while True:
        try:
            # Lấy input từ người dùng (chỉ ở đây, không ở file khác)
            user_input = input("\nBạn: ")
            
            # Kiểm tra điều kiện thoát trước khi xử lý
            if user_input.lower() in ['tạm biệt', 'thoát', 'bye', 'exit', 'quit']:
                utils.exit_chat(chat_history)
                break
            
            # PHÂN TÍCH Ý ĐỊNH NGAY LẬP TỨC sau khi nhận input
            response_text, summary, ticket_data = utils.get_response(
                chain=chain,
                chat_history=chat_history,
                question=user_input,
                context=context
            )
            
            # ĐIỀU HƯỚNG NGAY LẬP TỨC dựa trên summary vừa phân tích
            if summary == 'tạo ticket':
                # Tạo context chuyên biệt cho việc tạo ticket
                create_context = config.CREATE_CONTEXT
                # Gọi hàm create ticket với input hiện tại
                response_text, summary, ticket_data = create.create_ticket(chain, chat_history, user_input, create_context, response_text, summary, ticket_data)
                
            elif summary == 'sửa ticket':
                # Tạo context chuyên biệt cho việc sửa ticket
                edit_context = config.EDIT_CONTEXT
                # Gọi hàm edit ticket với input hiện tại
                response_text, summary, ticket_data = edit.edit_ticket(chain, chat_history, user_input, edit_context, response_text, summary, ticket_data)
                
            elif summary in ['tạm biệt', 'thoát']:
                # Lưu tin nhắn trước khi thoát
                chat_history.add_user_message(user_input)
                chat_history.add_ai_message(response_text)
                print("Chatbot: Tạm Biệt! Cảm ơn bạn đã sử dụng dịch vụ của mình")
                utils.exit_chat(chat_history)
                break
            
            # Lưu tin nhắn vào lịch sử (cho tất cả trường hợp)
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(response_text)
            
        except KeyboardInterrupt:
            print("\n\nCuộc trò chuyện bị ngắt bởi người dùng.")
            utils.exit_chat(chat_history)
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    start()
