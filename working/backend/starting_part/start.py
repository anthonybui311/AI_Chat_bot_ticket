from editing_part.edit import *
from creating_part.create import *

def start():
    print("Chào bạn! Mình là trợ lý hỗ trợ về ticket. Bạn muốn tạo ticket hay sửa nội dung ticket đã có")
    print("1. Tạo ticket")
    print("2. Sửa nội dung ticket")
    print("3. Thoát")
    choice = input("Bạn muốn làm gì? ")
    if choice == "1":
        create_ticket()
    elif choice == "2":
        edit_ticket()
    elif choice == "3":
        print("Cảm ơn bạn đã sử dụng dịch vụ của mình")