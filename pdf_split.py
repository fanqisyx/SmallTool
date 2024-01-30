import os
from PyPDF2 import PdfReader, PdfWriter
import tkinter as tk
from tkinter import filedialog

def subsplit(reader, start_page, end_page):
    output = PdfWriter()
    outfile = f"split_{start_page}-{end_page}.pdf"  # 分割后的文件

    for page_number in range(start_page - 1, end_page):
        if page_number < len(reader.pages):
            output.add_page(reader.pages[page_number])

    # 写入到目标PDF文件
    with open(outfile, "wb") as outputStream:
        output.write(outputStream)

    print(f"分割完成，保存为 {outfile}")


def on_submit():
    input_file_path = file_path_var.get()
    start_page = int(start_page_var.get())
    end_page = int(end_page_var.get())

    reader = PdfReader(open(input_file_path, "rb"))
    total_pages = len(reader.pages)

    if start_page < 1 or end_page > total_pages or start_page > end_page:
        result_label.config(text="输入的页面范围不正确，请重新输入正确的页面范围。", fg="red")
        return

    subsplit(reader, start_page, end_page)
    result_label.config(text="分割完成。", fg="green")


# 创建主窗口
window = tk.Tk()
window.title("PDF 分割工具")

# 文件路径输入部分
file_path_label = tk.Label(window, text="请选择待分割的PDF文件：")
file_path_label.pack()

file_path_var = tk.StringVar()
file_path_entry = tk.Entry(window, textvariable=file_path_var, width=50)
file_path_entry.pack()

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    file_path_var.set(file_path)

browse_button = tk.Button(window, text="浏览", command=browse_file)
browse_button.pack()

# 起始和终止页面输入部分
start_page_label = tk.Label(window, text="请输入起始页面：")
start_page_label.pack()

start_page_var = tk.StringVar()
start_page_entry = tk.Entry(window, textvariable=start_page_var)
start_page_entry.pack()

end_page_label = tk.Label(window, text="请输入终止页面：")
end_page_label.pack()

end_page_var = tk.StringVar()
end_page_entry = tk.Entry(window, textvariable=end_page_var)
end_page_entry.pack()

# 提交按钮
submit_button = tk.Button(window, text="开始分割", command=on_submit)
submit_button.pack()

# 显示结果的标签
result_label = tk.Label(window, text="", fg="black")
result_label.pack()

window.mainloop()
