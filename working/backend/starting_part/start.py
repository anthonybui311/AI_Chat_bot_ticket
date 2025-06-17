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

def start():
    """
    Hàm chính điều khiển toàn bộ luồng chatbot:
    - Khởi tạo chain, chat history và stage manager 
    - Chạy vòng lặp chính với stage management 
    - Phân tích ý định và điều hướng với state persistence 
    - Duy trì lịch sử hội thoại liên tục
    """
    print("Chatbot được khởi động. Nhập 'tạm biệt' hoặc 'thoát' để kết thúc cuộc trò chuyện.")
    
    # Khởi tạo chain, chat history và stage manager
    chain = utils.create_chain()
    chat_history = utils.ChatHistory()
    stage_manager = utils.StageManager()  # NEW: Quản lý trạng thái stage
    
    # Hiển thị câu chào đầu tiên
    
    while True:
        try:
            # Lấy input từ người dùng
            user_input = input(f"\n[{stage_manager.current_stage.upper()}] Bạn: ")
            
            # Kiểm tra điều kiện thoát trước khi xử lý
            if user_input.lower() in ['tạm biệt', 'thoát', 'bye', 'exit', 'quit']:
                utils.exit_chat(chat_history)
                print("Chatbot: Tạm Biệt! Cảm ơn bạn đã sử dụng dịch vụ của mình")
                print(f"Cuộc trò chuyện đã được lưu vào file: {chat_history.session_filename}")
                break
            
            # Lấy context tương ứng với stage hiện tại
            current_context = stage_manager.get_current_context()
            
            # PHÂN TÍCH Ý ĐỊNH với context phù hợp
            response_text, summary = utils.get_response(
                chain=chain,
                chat_history=chat_history,
                question=user_input,
                context=current_context
            )
            
            print(f"[DEBUG] Current stage: {stage_manager.current_stage}, Summary: {summary}")
            
            # ĐIỀU HƯỚNG dựa trên summary và stage hiện tại
            final_response, final_summary = utils.route_to_stage(
                stage_manager, response_text, summary, user_input, chain, chat_history
            )
            
            # Xử lý thoát nếu được yêu cầu
            if final_summary == 'thoát':
                chat_history.add_user_message(user_input)
                chat_history.add_ai_message(final_response)
                print(f"Chatbot: {final_response}")
                print(f"Cuộc trò chuyện đã được lưu vào file: {chat_history.session_filename}")
                utils.exit_chat(chat_history)
                break
            
            # Lưu tin nhắn vào lịch sử
            chat_history.add_user_message(user_input)
            chat_history.add_ai_message(final_response)
            
            # Hiển thị phản hồi
            print(f"Chatbot: {final_response}")
            print(f"[DEBUG] Final Summary: {final_summary}")
            
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