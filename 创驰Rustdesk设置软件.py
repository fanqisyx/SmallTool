import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import toml

class TomlEditor:
    def __init__(self, root, toml_file_path):
        self.root = root
        self.root.title("TOML Editor")
        self.root.geometry("400x250")  # Set a fixed window size
        self.toml_file_path = toml_file_path

        self.check_file_existence()  # Check if the file exists

        self.load_toml_data()
        self.create_widgets()

    def check_file_existence(self):
        if not os.path.isfile(self.toml_file_path):
            response = messagebox.showinfo("文件未找到", "软件未安装.\n配置文件不存在.\n请安装 Rustdesk 软件.")
            if response == "ok":
                self.root.destroy()  # Close the application if the file doesn't exist

    def load_toml_data(self):
        try:
            with open(self.toml_file_path, 'r') as file:
                self.config_data = toml.load(file)
        except FileNotFoundError:
            # Handle the case where the file doesn't exist yet
            self.config_data = {}

    def save_toml_data(self):
        with open(self.toml_file_path, 'w') as file:
            toml.dump(self.config_data, file)
        self.root.destroy()  # Close the application after saving

    def create_widgets(self):
        # Create and pack input fields
        ttk.Label(self.root, text="ID:").pack(pady=5)
        self.id_entry = ttk.Entry(self.root)
        self.id_entry.insert(0, self.config_data.get('id', ''))
        self.id_entry.pack(pady=5)

        ttk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show='*')
        self.password_entry.insert(0, self.config_data.get('password', ''))
        self.password_entry.pack(pady=5)

        ttk.Label(self.root, text="IP Address:").pack(pady=5)
        self.ip_entry = ttk.Entry(self.root)
        self.ip_entry.insert(0, str(self.config_data.get('keys_confirmed', {}).get('36.153.104.106', '')))
        self.ip_entry.pack(pady=5)

        # Create and pack Save button
        ttk.Button(self.root, text="Save", command=self.save_values).pack(pady=10)

    def save_values(self):
        # Update values in config_data
        self.config_data['id'] = self.id_entry.get()
        self.config_data['password'] = self.password_entry.get()
        self.config_data['key_confirmed'] = True

        
        self.config_data.setdefault('keys_confirmed', {})
        self.config_data['keys_confirmed']['36.153.104.106'] = bool(self.ip_entry.get())

        # Set default values
        self.config_data['keys_confirmed']['rs-ny'] = True


        # Delete 'enc_id' and 'key_pair' fields
        if 'enc_id' in self.config_data:
            del self.config_data['enc_id']

        if 'key_pair' in self.config_data:
            del self.config_data['key_pair']

        # Clear 'salt' field
        self.config_data['salt'] = ''

        # Save to TOML file
        self.save_toml_data()

if __name__ == "__main__":
    # 示例文件路径
    toml_file_path = 'C:\Windows\ServiceProfiles\LocalService\AppData\Roaming\RustDesk\config\RustDesk.toml'

    # 创建 Tkinter 窗口
    root = tk.Tk()
    
    # 创建 TomlEditor 实例
    editor = TomlEditor(root, toml_file_path)

    # 运行 Tkinter 事件循环
    root.mainloop()
