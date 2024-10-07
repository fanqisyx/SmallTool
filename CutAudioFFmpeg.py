import os
import subprocess
import threading
import multiprocessing
import re
import tkinter as tk
from tkinter import Label, Button, Entry, IntVar, BooleanVar, filedialog, messagebox, Checkbutton


class AudioSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("音频分割器")
        self.file_path = ""
        self.max_threads = multiprocessing.cpu_count()  # 获取CPU核心数

        # Tkinter变量
        self.segment_duration = IntVar()
        self.allow_overlap = BooleanVar()
        self.thread_count = IntVar(value=self.max_threads)  # 默认值设为CPU核心数

        self.create_widgets()

    def create_widgets(self):
        # 选择文件部分
        Label(self.root, text="请选择音频或视频文件：", font=("Arial", 12)).pack(pady=10)

        self.button_select = Button(self.root, text="选择文件", command=self.select_file)
        self.button_select.pack(pady=5)

        self.file_info_label = Label(self.root, text="未选择文件", fg="blue", font=("Arial", 10))
        self.file_info_label.pack(pady=10)

        # 音频时长显示
        self.label_duration = Label(self.root, text="音频时长: 未知", fg="blue", font=("Arial", 10))
        self.label_duration.pack(pady=10)

        # 分割参数设置
        Label(self.root, text="分割参数设置", font=("Arial", 12)).pack(pady=10)

        Label(self.root, text="每段文件时长（秒）：", font=("Arial", 10)).pack()
        self.segment_duration_entry = Entry(self.root, textvariable=self.segment_duration)
        self.segment_duration_entry.pack(pady=5)

        Label(self.root, text=f"最大线程数（最多{self.max_threads}核）：", font=("Arial", 10)).pack()
        self.thread_count_entry = Entry(self.root, textvariable=self.thread_count)
        self.thread_count_entry.pack(pady=5)

        # 绑定输入框的验证函数，限制线程数最大值
        self.thread_count_entry.bind("<KeyRelease>", self.validate_thread_count)

        # 重叠选项
        self.allow_overlap_check = Checkbutton(self.root, text="允许文件间重叠 3 秒", variable=self.allow_overlap)
        self.allow_overlap_check.pack(pady=5)

        # 开始分割按钮
        self.button_split = Button(self.root, text="开始分割", command=self.split_audio)
        self.button_split.pack(pady=20)

        # 进度信息显示
        self.progress_label = Label(self.root, text="", fg="green", font=("Arial", 10))
        self.progress_label.pack(pady=10)

        self.result_label = Label(self.root, text="", fg="green", font=("Arial", 10))
        self.result_label.pack(pady=10)

    def validate_thread_count(self, event):
        value = self.thread_count_entry.get()
        # 只允许输入数字
        if not value.isdigit() and value != "":
            self.thread_count_entry.delete(0, tk.END)
            self.thread_count_entry.insert(0, value[:-1])  # 删除最后一个字符
        else:
            # 如果数字大于核心数，则重置为核心数
            if int(value) > self.max_threads:
                self.thread_count_entry.delete(0, tk.END)
                self.thread_count_entry.insert(0, str(self.max_threads))

    def select_file(self):
        self.file_path = filedialog.askopenfilename(title="选择音频或视频文件",
                                        filetypes=[("音频文件", "*.mp3;*.wav;*.aac;*.flac;*.ogg"),
                                                   ("视频文件", "*.mp4;*.mkv;*.avi;*.mov"),
                                                   ("所有文件", "*.*")])
        if self.file_path:
            # 显示音频时长
            duration = self.get_audio_duration(self.file_path)
            self.file_info_label.config(text=f"已选择文件: {self.file_path}")
            self.label_duration.config(text=f"音频时长: {duration} 秒")

    def get_audio_duration(self, input_file):
        """获取音频文件时长（秒）"""
        command = ['ffmpeg', '-i', input_file]
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True, encoding='utf-8')

        # 查找包含 "Duration" 的行
        duration_line = None
        for line in result.stderr.splitlines():
            if 'Duration' in line:
                duration_line = line
                break

        if duration_line is None:
            messagebox.showerror("错误", "无法获取音频文件时长。请检查文件格式是否支持。")
            return 0  # 返回 0 或其他默认值

        # 解析持续时间
        try:
            duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', duration_line)
            if duration_match:
                hours, minutes, seconds = map(float, duration_match.groups())
                total_seconds = int(hours * 3600 + minutes * 60 + seconds)
                return total_seconds
            else:
                raise ValueError("无法解析时长")
        except Exception as e:
            messagebox.showerror("错误", f"解析时长时发生错误: {e}")
            return 0  # 返回 0 或其他默认值

    # 输入线程数时限制最大值
    def validate_thread_count(self, event):
        max_value = self.max_threads
        try:
            value = int(self.thread_count_entry.get())
            if value > max_value:
                self.thread_count_entry.delete(0, 'end')
                self.thread_count_entry.insert(0, str(max_value))
        except ValueError:
            self.thread_count_entry.delete(0, 'end')
            self.thread_count_entry.insert(0, str(max_value))

    def split_audio(self):
        if not self.file_path:
            messagebox.showerror("错误", "请先选择音频文件！")
            return

        segment_duration = self.segment_duration.get()
        total_duration = self.get_audio_duration(self.file_path)

        num_segments = total_duration // segment_duration + (1 if total_duration % segment_duration else 0)
        self.progress_label.config(text=f"总共将生成 {num_segments} 个文件。")

        threads = []
        max_threads = min(self.thread_count.get(), self.max_threads)

        for i in range(num_segments):
            start_time = i * segment_duration
            overlap_duration = 3 if self.allow_overlap.get() else 0
            duration = segment_duration + overlap_duration

            if start_time + duration > total_duration:
                duration = total_duration - start_time

            output_file = f"{os.path.splitext(self.file_path)[0]}_part{str(i + 1).zfill(4)}_{start_time}_{start_time + duration}.mp3"
            thread = threading.Thread(target=self.run_ffmpeg, args=(start_time, duration, output_file))
            threads.append(thread)

            if len(threads) >= max_threads:
                threads[0].join()
                threads.pop(0)

            thread.start()
            self.progress_label.config(text=f"正在生成文件 {i + 1}/{num_segments}：{output_file}")
            self.root.update()  # 更新界面

        for thread in threads:
            thread.join()
            self.root.update()  # 更新界面

        messagebox.showinfo("完成", f"分割完成，共生成 {num_segments} 个文件。")

    def run_ffmpeg(self, start_time, duration, output_file):
        command = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", self.file_path,
            "-t", str(duration),
            "-q:a", "0",  # 设置音频质量
            "-map", "a",  # 只提取音频
            output_file
        ]
        subprocess.run(command, stderr=subprocess.PIPE)


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitter(root)
    root.mainloop()
