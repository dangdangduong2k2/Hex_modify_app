import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import time

class FlashToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Microcontroller Flash Tool")
        self.root.geometry("400x320")  # Adjust the window size to accommodate the new field

        self.tool_path = self.detect_tool_path()
        self.file_path = tk.StringVar()
        self.code_size = tk.StringVar()
        self.uid = tk.StringVar()
        self.cpu = tk.StringVar()

        tk.Label(root, text="Hex File Path:").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.file_path, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(root, text="Code Size:").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.code_size, width=30, state='readonly').grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="UID:").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.uid, width=30, state='readonly').grid(row=2, column=1, padx=5, pady=5)

        tk.Label(root, text="CPU:").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(root, textvariable=self.cpu, width=30, state='readonly').grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(root, text="Get", command=self.get_info).grid(row=2, column=2, rowspan=2, padx=5, pady=5)

        ttk.Button(root, text="Flash", command=self.flash_microcontroller).grid(row=4, column=0, padx=5, pady=5)
        ttk.Button(root, text="Erase", command=self.erase_microcontroller).grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(root, text="Reset", command=self.reset_microcontroller).grid(row=4, column=2, padx=5, pady=5)

        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.map("TButton", background=[('active', '#0052cc')], foreground=[('active', 'white')])

    def detect_tool_path(self):
        default_path = r"C:\Program Files (x86)\Nuvoton Tools\NuLink Command Tool\NuLink_8051OT.exe"
        if os.path.exists(default_path):
            return default_path
        else:
            messagebox.showerror("Error", "NuLink tool not found. Please locate the tool manually.")
            return filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Hex files", "*.hex")])
        if file_path:
            self.file_path.set(file_path)

    

    def erase_microcontroller(self):
        if self.tool_path:
            command = [self.tool_path, "-e", "ALL"]
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Ensure the NuLink tool path is correct.")

    def reset_microcontroller(self):
        if self.tool_path:
            command = [self.tool_path, "-reset"]
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Ensure the NuLink tool path is correct.")
    def flash_microcontroller(self):
        self.erase_microcontroller()
        self.reset_microcontroller ()
        hex_file = self.file_path.get()
        if hex_file and self.tool_path:
            command = [self.tool_path, "-w", "APROM", hex_file]
            self.run_command(command)
        else:
            messagebox.showerror("Error", "Please select a hex file and ensure the NuLink tool path is correct.")
    def get_info(self):
        self.get_code_size()
        self.get_uid()
        self.get_cpu()

    def get_code_size(self):
        hex_file = self.file_path.get()
        if hex_file:
            code_size = self.calculate_code_size(hex_file)
            self.code_size.set(f"{code_size} bytes")
        else:
            self.code_size.set("")

    def calculate_code_size(self, hex_file):
        code_size = 0
        with open(hex_file, 'r') as file:
            for line in file:
                if line.startswith(':'):
                    byte_count = int(line[1:3], 16)
                    code_size += byte_count
        return code_size

    def get_uid(self):
        if self.tool_path:
            command = [self.tool_path, "-r", "UID"]
            output = self.run_command(command)
            self.uid.set(output)
        else:
            messagebox.showerror("Error", "Ensure the NuLink tool path is correct.")

    def get_cpu(self):
        if self.tool_path:
            command = [self.tool_path, "-p"]
            output = self.run_command(command)
            self.cpu.set(output)
        else:
            messagebox.showerror("Error", "Ensure the NuLink tool path is correct.")

    def run_command(self, command):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            output = result.stdout
            message = self.extract_message(output)
            return message
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr)
            return ""

    def extract_message(self, output):
        lines = output.splitlines()
        relevant_lines = [line.split('>>>')[-1].strip() for line in lines if '>>>' in line]
        if len(relevant_lines) >= 2:
            message = relevant_lines[1]
            if 'UID:' in message:
                return message.split('UID:')[-1].strip()
            return message
        return "Unknown response"

if __name__ == "__main__":
    root = tk.Tk()
    app = FlashToolGUI(root)
    root.mainloop()
