# ...existing code...

# if __name__ == "__main__":
#     from gui import FlashToolGUI
#     import tkinter as tk

#     root = tk.Tk()
#     app = FlashToolGUI(root)
#     root.mainloop()
from intelhex import IntelHex

# Đường dẫn tới file hex gốc và file hex mới
original_hex_path = r"C:/onedrive/0973210690 KH anh Trung/mach 2 tang mini V2/Code/250225/Objects/V2_Mini.hex"
output_hex_path = r"C:/onedrive/0973210690 KH anh Trung/mach 2 tang mini V2/Code/250225/Objects/a.hex"

# Tạo dữ liệu mới cho struct eeprom_type (48 byte: byte đầu = 0x00, còn lại = 0x01)
new_data = [
    0x01,                   # init
    0x00, 0x09,            # time[COOL][CL] = 5
    0x00, 0x05,            # time[COOL][OP] = 5
    0x00, 0x3C,            # time[ICE_FLUSH][CL] = 60
    0x00, 0x06,            # time[ICE_FLUSH][OP] = 6
    0x00, 0x07,            # delayST = 7
    0x00,                  # ST[LCD] = 0
    0x19,                  # ST[LED] = 25
    0x00, 0x00,            # DF = 0
    0x01,                  # END = 1
    0x01,                  # first_progress = OP
    0x00,                  # mode = LCD
    0x00, 0x01,            # set[BRIGHTNESS_GREEN] = 1
    0x00, 0x01,            # set[BRIGHTNESS_RED] = 1
    0x00, 0x00,            # autoshutdown = 0
    0x01,                  # touch_num = 1
    0xE7, 0x03,            # lock_time = 999
    0x00, 0x00,            # password[0] = 0
    0x00, 0x00,            # password[1] = 0
    0x00, 0x00,            # password[2] = 0
    0x00, 0x00,            # password[3] = 0
    0x00, 0x00,            # password[4] = 0
    0x00, 0x00,            # password[5] = 0
    0x00, 0x00, 0x00, 0x00,  # user_password = 0
    0x00,                  # user_init = 0
    0x00, 0x00, 0x00, 0x00,  # user_timeout = 0
    0x01,                  # DF_unit = SECOND
    0x00                   # hide_mode_SL_END = SHOW
]

# Đọc file hex gốc
hex_file = IntelHex(original_hex_path)

# Địa chỉ bắt đầu ghi đè
start_address = 0x7F00  # đổi từ 0x7F00 thành 0x7E00

# Ghi đè dữ liệu vào vùng địa chỉ 0x7E00
for i, value in enumerate(new_data):
    hex_file[start_address + i] = value

# Ghi ra file hex mới
hex_file.write_hex_file(output_hex_path)

# Thông báo đã hoàn thành
print("ok")

