import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
from intelhex import IntelHex
import os

class FlashToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Microcontroller Flash Tool")
        self.root.geometry("600x1000")  # Increased size for better layout
        self.root.resizable(False, False)

        self.tool_path = self.detect_tool_path()
        self.file_path = tk.StringVar()
        self.eeprom_entries = []
        self.multi_byte_entries = {}  # Track entries that need byte splitting
        self.EEPROM_START_ADDRESS = 0x7F00  # Changed to correct EEPROM address

        # File selection frame
        file_frame = ttk.LabelFrame(root, text="File Selection")
        file_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(file_frame, text="Hex File:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(file_frame, textvariable=self.file_path).grid(row=0, column=1, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

        # Control buttons frame
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(btn_frame, text="Flash", command=self.flash_microcontroller).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Erase", command=self.erase_microcontroller).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_microcontroller).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save & Flash", command=self.save_and_flash).pack(side="right", padx=5)

        # EEPROM data frame
        eeprom_frame = ttk.LabelFrame(root, text="EEPROM Configuration")
        eeprom_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.eeprom_entries = []
        row = 0

        # Init byte (uint8_t)
        self.add_entry_field(eeprom_frame, row, "Init:", 1, default="0")
        row += 1

        # Time settings (uint16_t[2][2])
        time_frame = ttk.LabelFrame(eeprom_frame, text="Time Settings")
        time_frame.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self.add_entry_field(time_frame, 0, "Chạy lạnh CL (Time[0][0]):", 1, is_uint16=True, default="5")
        self.add_entry_field(time_frame, 1, "Chạy lạnh OP (Time[0][1]):", 1, is_uint16=True, default="5")
        self.add_entry_field(time_frame, 2, "Xả đá CL (Time[1][0]):", 1, is_uint16=True, default="60")
        self.add_entry_field(time_frame, 3, "Xả đá OP (Time[1][1]):", 1, is_uint16=True, default="6")
        row += 1

        # Delay ST (uint16_t)
        self.add_entry_field(eeprom_frame, row, "Delay ST (100ms):", 1, is_uint16=True, default="7")
        row += 1

        # ST settings (uint8_t[2])
        st_frame = ttk.LabelFrame(eeprom_frame, text="ST Settings")
        st_frame.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self.add_entry_field(st_frame, 0, "ST LCD:", 1, default="0")
        self.add_entry_field(st_frame, 1, "ST Led:", 1, default="25")
        row += 1

        # DF settings (uint16_t)
        self.add_entry_field(eeprom_frame, row, "DF value:", 1, is_uint16=True, default="0")
        row += 1

        # END, First Progress, Mode
        self.add_entry_field(eeprom_frame, row, "END:", 1, default="1")
        row += 1
        self.add_entry_field(eeprom_frame, row, "First Progress:", 1, default="1") # OP = 1
        row += 1
        self.add_entry_field(eeprom_frame, row, "Mode SL:", 1, default="0") # LCD = 0
        row += 1

        # Set values (uint16_t[2])
        led_frame = ttk.LabelFrame(eeprom_frame, text="LED Brightness")
        led_frame.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self.add_entry_field(led_frame, 0, "Độ sáng led xanh (Set[0]):", 1, is_uint16=True, default="1")
        self.add_entry_field(led_frame, 1, "Độ sáng led đỏ (Set[1]):", 1, is_uint16=True, default="1")
        row += 1

        # Auto shutdown (uint16_t)
        self.add_entry_field(eeprom_frame, row, "Try days (Auto shutdown):", 1, is_uint16=True, default="0")
        row += 1

        # Touch num (uint8_t)
        self.add_entry_field(eeprom_frame, row, "Số lần nhấn (Touch num):", 1, default="1")
        row += 1

        # Lock time (uint16_t)
        self.add_entry_field(eeprom_frame, row, "Auto lock (Lock time):", 1, is_uint16=True, default="999")
        row += 1

        # Password settings (uint16_t[6])
        pwd_frame = ttk.LabelFrame(eeprom_frame, text="Password Configuration")
        pwd_frame.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        for i in range(6):
            self.add_entry_field(pwd_frame, i, f"Password[{i}]:", 1, is_uint16=True, default="0")
        row += 1

        # User settings
        user_frame = ttk.LabelFrame(eeprom_frame, text="User Settings")
        user_frame.grid(row=row, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self.add_entry_field(user_frame, 0, "User Password:", 1, is_uint32=True, default="0")
        self.add_entry_field(user_frame, 1, "User Init:", 1, default="0")
        self.add_entry_field(user_frame, 2, "User Timeout:", 1, is_uint32=True, default="0")
        row += 1

        # Final settings
        self.add_entry_field(eeprom_frame, row, "dF unit:", 1, default="0") # SECOND = 0
        row += 1
        self.add_entry_field(eeprom_frame, row, "Hide Mode SL END:", 1, default="0") # SHOW = 0

    def add_entry_field(self, parent, row, label, display_width=1, column=0, is_uint16=False, is_uint32=False, default="0"):
        tk.Label(parent, text=label).grid(row=row, column=column, padx=5, pady=2, sticky="e")
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column+1, padx=5, pady=2, sticky="w")
        
        entry = tk.Entry(frame, width=6 if is_uint16 else (10 if is_uint32 else 4))
        entry.pack(side="left", padx=1)
        entry.delete(0, tk.END)
        entry.insert(0, default)
        
        if is_uint16 or is_uint32:
            self.multi_byte_entries[len(self.eeprom_entries)] = {
                'entry': entry,
                'bytes': 4 if is_uint32 else 2
            }
            # Add placeholder entries for the actual bytes
            for _ in range(4 if is_uint32 else 2):
                self.eeprom_entries.append(None)
        else:
            self.eeprom_entries.append(entry)

    def get_entry_bytes(self, value, num_bytes):
        """Convert decimal input to specified number of bytes in big endian"""
        try:
            value = int(value)
            bytes_list = []
            for i in range(num_bytes):
                # MSB first for big endian, so we need to reverse the list later
                bytes_list.append(value & 0xFF)
                value >>= 8
            return bytes_list[::-1]  # Reverse list to get big endian order
        except ValueError:
            return [0] * num_bytes

    def detect_tool_path(self):
        default_path = r"C:\\Program Files (x86)\\Nuvoton Tools\\NuLink Command Tool\\NuLink_8051OT.exe"
        if os.path.exists(default_path):
            return default_path
        else:
            messagebox.showerror("Error", "NuLink tool not found. Please locate the tool manually.")
            return filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Hex files", "*.hex")])
        if file_path:
            self.file_path.set(file_path)
            try:
                hex_file = IntelHex(file_path)
                # Read and combine multi-byte values in big endian
                for idx, entry_info in self.multi_byte_entries.items():
                    value = 0
                    for i in range(entry_info['bytes']):
                        addr = self.EEPROM_START_ADDRESS + idx + i
                        try:
                            # For big endian: MSB at lowest address
                            byte_shift = ((entry_info['bytes'] - 1) - i) * 8
                            value |= hex_file[addr] << byte_shift
                        except:
                            pass
                    entry_info['entry'].delete(0, tk.END)
                    entry_info['entry'].insert(0, str(value))
                
                # Handle single-byte entries
                for i, entry in enumerate(self.eeprom_entries):
                    if entry and i not in self.multi_byte_entries:
                        try:
                            value = hex_file[self.EEPROM_START_ADDRESS + i]
                            entry.delete(0, tk.END)
                            entry.insert(0, f"{value:02X}")
                        except:
                            pass
                            
                messagebox.showinfo("Success", "Hex file loaded")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load hex file:\n{e}")

    def save_and_flash(self):
        hex_file_path = self.file_path.get()
        if not hex_file_path:
            messagebox.showerror("Error", "Please select a HEX file first.")
            return

        try:
            # Process all entries and convert multi-byte values
            new_data = []
            current_idx = 0
            
            while current_idx < len(self.eeprom_entries):
                if current_idx in self.multi_byte_entries:
                    entry_info = self.multi_byte_entries[current_idx]
                    value = entry_info['entry'].get().strip()
                    bytes_list = self.get_entry_bytes(value, entry_info['bytes'])
                    new_data.extend(bytes_list)
                    current_idx += entry_info['bytes']
                else:
                    if self.eeprom_entries[current_idx]:
                        value = self.eeprom_entries[current_idx].get().strip()
                        new_data.append(int(value, 16) if value else 0)
                    current_idx += 1

            # Continue with existing hex file handling...
            hex_file = IntelHex(hex_file_path)
            for i, value in enumerate(new_data):
                addr = self.EEPROM_START_ADDRESS + i
                hex_file[addr] = value

            # Create temporary file with merged data
            temp_file = hex_file_path.replace('.hex', '_merged.hex')
            hex_file.write_hex_file(temp_file)

            # Flash the merged file
            if self.tool_path:
                self.erase_microcontroller()
                self.reset_microcontroller()
                command = [self.tool_path, "-w", "APROM", temp_file]
                result = self.run_command(command)
                if result:
                    messagebox.showinfo("Success", "File flashed successfully!")
                
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

        except ValueError as e:
            messagebox.showerror("Error", "Invalid input value")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge and flash:\n{e}")

    def erase_microcontroller(self):
        if self.tool_path:
            command = [self.tool_path, "-e", "ALL"]
            self.run_command(command)

    def reset_microcontroller(self):
        if self.tool_path:
            command = [self.tool_path, "-reset"]
            self.run_command(command)

    def flash_microcontroller(self):
        self.erase_microcontroller()
        self.reset_microcontroller()
        hex_file = self.file_path.get()
        if hex_file and self.tool_path:
            command = [self.tool_path, "-w", "APROM", hex_file]
            self.run_command(command)

    def get_info(self):
        pass

    def run_command(self, command):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr)
            return ""

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashToolGUI(root)
    root.mainloop()
