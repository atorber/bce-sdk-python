import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
from baidubce.services.aihc.aihc_client import generate_aiak_parameter
import json
import os
import pyperclip  # 用于复制到剪贴板
import re  # 用于正则表达式匹配
from itertools import zip_longest  # 用于正确处理最后不完整的参数组

# 确保安装了 pyperclip，可以使用以下命令安装：
# pip install pyperclip

# 输入参数
input_params = {
    "MODEL_NAME": "llama2-13b",
    "REPLICAS": "2",
    "VERSION": "v1",
    "TRAINING_PHASE": "pretrain",
    "TP": "",
    "PP": "",
    "DATASET_NAME": "WuDaoCorpus2.0_base_sample",
    "JSON_KEYS": "text",
    "IMAGE": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
    "MOUNT_PATH": "/workspace/pfs",
    "MODEL_URL": "",
    "DATASET_URL": "",
    "OUTPUT_DIR": "",  # 新增的参数
}

model_options = [
    "llama2-7b", "llama2-13b", "llama2-70b",
    "llama3-8b", "llama3-70b",
    "qwen2-0.5b", "qwen2-1.5b", "qwen2-7b", "qwen2-72b",
    "baichuan2-7b", "baichuan2-13b",
    "qwen-1.8b", "qwen-7b", "qwen-14b", "qwen-72b",
    "qwen1.5-0.5b", "qwen1.5-1.8b", "qwen1.5-4b",
    "qwen1.5-7b", "qwen1.5-14b", "qwen1.5-32b", "qwen1.5-72b"
]

# 定义哪些字段是必填的（排除 MODEL_URL 和 DATASET_URL）
required_fields = [key for key, value in input_params.items() if value and key not in ["MODEL_URL", "DATASET_URL"]]


def grouper(iterable, n, fillvalue=(None, None)):
    """Collect data into fixed-length chunks or blocks, filling missing values with `fillvalue`."""
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


class PlaceholderEntry(ttk.Entry):
    """Entry widget with placeholder text."""

    def __init__(self, master=None, placeholder="", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color

    def foc_in(self, *args):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['foreground'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class ParameterConfigApp:
    def __init__(self, root, params):
        self.sh_file = None  # 用于存储生成的脚本文件路径
        self.root = root
        self.root.title("AIAK-DESKTOP")
        self.params = params.copy()  # 保留初始参数
        self.entries = {}  # 存储每个参数对应的组件

        # 设置窗口大小和最小尺寸
        self.root.geometry("1000x800")
        self.root.minsize(800, 700)

        # 设置主题
        style = ttk.Style()
        style.theme_use("clam")  # 可选主题："clam", "alt", "default", "classic"

        # 创建主框架
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 使用Grid布局，6列（每个参数占两列：标签和输入）
        main_frame.columnconfigure(tuple(range(6)), weight=1)

        # 定义TRAINING_PHASE与对应的DATASET_NAME选项
        self.training_phase_options = ["pretrain", "sft"]
        self.dataset_options = {
            "pretrain": ["pile_llama_test", "WuDaoCorpus2.0_base_sample"],
            "sft": ["alpaca_zh-llama3-train", "alpaca_zh-llama3-valid"]
        }

        # 动态创建标签和输入组件，每行3个参数
        params_list = list(self.params.items())

        # 将 OUTPUT_DIR 移到最前面
        if "OUTPUT_DIR" in self.params:
            # 创建一个新的列表，将 "OUTPUT_DIR" 放在首位
            params_list = [("OUTPUT_DIR", self.params["OUTPUT_DIR"])] + [
                (k, v) for k, v in params_list if k != "OUTPUT_DIR"
            ]

        for row, param_group in enumerate(grouper(params_list, 3)):
            for col, (key, value) in enumerate(param_group):
                if key is None:
                    continue  # 如果参数不足3的倍数，跳过

                # 计算实际的列位置
                label_col = col * 2
                entry_col = col * 2 + 1

                # 检查是否为必填项
                is_required = key in required_fields

                # 标签
                if is_required:
                    label_text = f"{key} *"
                    label = ttk.Label(main_frame, text=label_text, font=("Helvetica", 12, "bold"), foreground="red")
                else:
                    label_text = key
                    label = ttk.Label(main_frame, text=label_text, font=("Helvetica", 12, "bold"))
                label.grid(row=row, column=label_col, padx=10, pady=10, sticky=tk.W)

                # 根据key创建不同类型的输入组件
                if key == "OUTPUT_DIR":
                    # 目录选择，包含文本框和浏览按钮
                    frame = ttk.Frame(main_frame)
                    frame.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)

                    entry = ttk.Entry(frame, width=40, font=("Helvetica", 12))
                    entry.pack(side=tk.LEFT, padx=(0, 5))
                    entry.insert(0, value)
                    self.entries[key] = entry

                    browse_button = ttk.Button(frame, text="浏览", command=lambda e=entry: self.browse_directory(e))
                    browse_button.pack(side=tk.LEFT)
                elif key == "TRAINING_PHASE":
                    # 单选按钮
                    self.training_phase_var = tk.StringVar(value=value)
                    frame = ttk.Frame(main_frame)
                    frame.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    ttk.Radiobutton(frame, text="Pretrain", variable=self.training_phase_var, value="pretrain", command=self.update_dataset_options).pack(side=tk.LEFT, padx=5)
                    ttk.Radiobutton(frame, text="SFT", variable=self.training_phase_var, value="sft", command=self.update_dataset_options).pack(side=tk.LEFT, padx=5)
                    self.entries[key] = self.training_phase_var
                elif key == "REPLICAS":
                    # 数字输入，限制为整数 >=1
                    vcmd = (self.root.register(self.validate_positive_integer), '%P')
                    entry = ttk.Entry(main_frame, width=20, font=("Helvetica", 12), validate='key', validatecommand=vcmd)
                    entry.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[key] = entry
                elif key == "MODEL_NAME":
                    # 下拉选项
                    combobox = ttk.Combobox(main_frame, values=model_options, state="readonly", font=("Helvetica", 12))
                    combobox.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    combobox.set(value if value in model_options else model_options[0])
                    self.entries[key] = combobox
                elif key == "DATASET_NAME":
                    # 下拉选项，根据TRAINING_PHASE动态变化
                    self.dataset_name_var = tk.StringVar()
                    combobox = ttk.Combobox(main_frame, textvariable=self.dataset_name_var, state="readonly", font=("Helvetica", 12))
                    combobox.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    # 设置初始选项
                    current_phase = self.params.get("TRAINING_PHASE", "pretrain")
                    combobox['values'] = self.dataset_options.get(current_phase, [])
                    combobox.set(value if value in combobox['values'] else (combobox['values'][0] if combobox['values'] else ""))
                    self.entries[key] = combobox
                elif key in ["TP", "PP"]:
                    # 数字输入，限制为正整数
                    vcmd_tp_pp = (self.root.register(self.validate_positive_integer), '%P')
                    entry = ttk.Entry(main_frame, width=20, font=("Helvetica", 12), validate='key', validatecommand=vcmd_tp_pp)
                    entry.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[key] = entry
                elif key in ["MODEL_URL", "DATASET_URL"]:
                    # 文本输入，必须以bos:/开头（选填）
                    entry = PlaceholderEntry(main_frame, placeholder="以 bos:/ 开头", width=30, font=("Helvetica", 12))
                    entry.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[key] = entry
                elif key == "VERSION":
                    # 默认文本输入框，带有特定校验
                    vcmd_version = (self.root.register(self.validate_version), '%P')
                    entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12), validate='key', validatecommand=vcmd_version)
                    entry.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[key] = entry
                else:
                    # 默认文本输入框
                    entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
                    entry.grid(row=row, column=entry_col, padx=10, pady=10, sticky=tk.W)
                    entry.insert(0, value)
                    self.entries[key] = entry

        # 按钮框架
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=(len(params_list) // 3), column=0, columnspan=6, pady=20)

        # 生成按钮
        generate_button = ttk.Button(button_frame, text="生成命令", command=self.save_params)
        generate_button.pack(side=tk.LEFT, padx=20, ipadx=10, ipady=5)

        # 重置按钮
        reset_button = ttk.Button(button_frame, text="重置", command=self.reset_params)
        reset_button.pack(side=tk.LEFT, padx=20, ipadx=10, ipady=5)

        # 复制按钮
        copy_button = ttk.Button(button_frame, text="复制到剪切板", command=self.copy_sh_file, state='disabled')
        copy_button.pack(side=tk.LEFT, padx=20, ipadx=10, ipady=5)
        self.copy_button = copy_button  # 存储按钮实例以便后续启用/禁用

        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="10")
        log_frame.grid(row=(len(params_list) // 3) + 1, column=0, columnspan=6, padx=10, pady=10, sticky=tk.NSEW)

        # 配置日志区域可扩展
        main_frame.rowconfigure((len(params_list) // 3) + 1, weight=1)
        main_frame.columnconfigure(5, weight=1)  # 最后一列扩展

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20, font=("Courier", 10), state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 初始化 DATASET_NAME 选项
        self.update_dataset_options()

    def browse_directory(self, entry_widget):
        """打开目录选择对话框并设置选定的目录到对应的Entry中"""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_dir)
            self.log_message(f"选择的目录: {selected_dir}")

    def update_dataset_options(self):
        """根据TRAINING_PHASE更新DATASET_NAME的选项"""
        selected_phase = self.training_phase_var.get()
        dataset_combobox = self.entries.get("DATASET_NAME")
        if dataset_combobox:
            new_options = self.dataset_options.get(selected_phase, [])
            dataset_combobox['values'] = new_options
            # 如果当前选中的值不在新的选项中，则重置
            current_value = dataset_combobox.get()
            if current_value not in new_options:
                dataset_combobox.set(new_options[0] if new_options else "")
            self.log_message(f"TRAINING_PHASE 改变为 {selected_phase}，更新 DATASET_NAME 选项为: {new_options}")

    def validate_positive_integer(self, P):
        """验证输入是否为正整数"""
        if P == "":
            return True  # 允许清空，由必填项校验处理
        if P.isdigit() and int(P) > 0:
            return True
        else:
            self.root.bell()  # 发出提示音
            return False

    def validate_version(self, P):
        """验证VERSION输入，只允许小写字母、数字和连字符，长度1-30，结尾必须是小写字母或数字"""
        if P == "":
            return True  # 允许清空，由必填项校验处理
        pattern = re.compile(r'^[a-z0-9]([a-z0-9\-]{0,28}[a-z0-9])?$')
        if pattern.match(P):
            return True
        else:
            self.root.bell()  # 发出提示音
            return False

    def save_params(self):
        """保存用户输入的参数并记录日志，同时进行必填项和特定字段校验"""
        updated_params = {}
        missing_fields = []
        invalid_fields = []

        # Collect and validate inputs
        for key, entry in self.entries.items():
            if key == "TRAINING_PHASE":
                updated_params[key] = entry.get()
            elif key == "OUTPUT_DIR":
                updated_params[key] = entry.get()
            elif key in ["REPLICAS", "TP", "PP"]:
                updated_params[key] = entry.get()
            elif key in ["MODEL_URL", "DATASET_URL"]:
                updated_params[key] = entry.get()
            elif key == "VERSION":
                updated_params[key] = entry.get()
            else:
                updated_params[key] = entry.get()

        # 检查必填项是否填写
        for field in required_fields:
            value = updated_params.get(field, "").strip()
            if not value or (field in ["MODEL_URL", "DATASET_URL"] and value == "以 bos:/ 开头"):
                missing_fields.append(field)

        # 检查特定字段的格式
        # VERSION 字段已经在 save_params 中进行了单独验证
        version = updated_params.get("VERSION", "").strip()
        version_pattern = re.compile(r'^[a-z0-9]([a-z0-9\-]{0,28}[a-z0-9])?$')
        if version and not version_pattern.match(version):
            invalid_fields.append("VERSION")

        # TP 和 PP 必须为正整数（如果有输入）
        for field in ["TP", "PP"]:
            value = updated_params.get(field, "").strip()
            if value and (not value.isdigit() or int(value) <= 0):
                invalid_fields.append(field)

        # MODEL_URL 和 DATASET_URL 必须以 bos:/ 开头（如果有输入）
        for field in ["MODEL_URL", "DATASET_URL"]:
            value = updated_params.get(field, "").strip()
            if value and not value.startswith("bos:/") and value != "以 bos:/ 开头":
                invalid_fields.append(field)

        # 检查 OUTPUT_DIR 是否存在且为目录
        chain_job_dir = updated_params.get("OUTPUT_DIR", "").strip()
        if not chain_job_dir:
            missing_fields.append("OUTPUT_DIR")
        elif not os.path.isdir(chain_job_dir):
            invalid_fields.append("OUTPUT_DIR")
            self.log_message(f"OUTPUT_DIR 路径无效或不存在：{chain_job_dir}")

        # 如果有缺少的必填项或格式错误的字段，提示用户
        error_messages = []
        if missing_fields:
            missing_str = ", ".join(missing_fields)
            error_messages.append(f"缺少必填项：{missing_str}")
            self.log_message(f"保存失败，缺少必填项：{missing_str}")

        if invalid_fields:
            invalid_str = ", ".join(invalid_fields)
            error_messages.append(f"以下字段格式不正确：{invalid_str}")
            self.log_message(f"保存失败，以下字段格式不正确：{invalid_str}")

        if error_messages:
            full_error_message = "\n".join(error_messages)
            messagebox.showerror("输入错误", full_error_message)
            return

        # 进一步验证字段格式
        # VERSION 字段已经验证过，恢复背景色
        version_entry = self.entries.get("VERSION")
        if isinstance(version_entry, ttk.Entry):
            version_entry.config(background='white')

        # TP 和 PP 验证
        for field in ["TP", "PP"]:
            entry = self.entries.get(field)
            if entry and (not entry.get().isdigit() or int(entry.get()) <= 0):
                entry.config(background='pink')
            else:
                if entry:
                    entry.config(background='white')

        # MODEL_URL 和 DATASET_URL 验证（仅在有输入时）
        for field in ["MODEL_URL", "DATASET_URL"]:
            entry = self.entries.get(field)
            value = updated_params.get(field, "").strip()
            if entry:
                if value and not value.startswith("bos:/"):
                    entry.config(background='pink')
                else:
                    entry.config(background='white')

        # OUTPUT_DIR 验证
        chain_job_entry = self.entries.get("OUTPUT_DIR")
        if chain_job_entry:
            chain_job_dir = chain_job_entry.get().strip()
            if not os.path.isdir(chain_job_dir):
                chain_job_entry.config(background='pink')
            else:
                chain_job_entry.config(background='white')

        # 更新内部参数字典
        self.params = updated_params.copy()

        # 记录日志
        self.log_message("保存参数成功")
        self.log_message(f"更新的参数：{self.params}")
        self.params['MODEL_URL'] = '' if self.params['MODEL_URL'] == '以 bos:/ 开头' else self.params['MODEL_URL']
        self.params['DATASET_URL'] = '' if self.params['DATASET_URL'] == '以 bos:/ 开头' else self.params['DATASET_URL']
        self.generate_parameter(json.dumps(self.params))

        # 如果sh_file已生成，启用“复制”按钮
        if self.sh_file and os.path.isfile(self.sh_file):
            self.copy_button.config(state='normal')
        else:
            self.copy_button.config(state='disabled')

        # 显示成功消息
        messagebox.showinfo("保存成功", "执行命令生成成功，可复制到剪贴板")

    def reset_params(self):
        """重置所有输入框到初始值"""
        for key, entry in self.entries.items():
            if key == "TRAINING_PHASE":
                entry.set(self.params[key])
            elif key == "MODEL_NAME":
                entry.set(self.params[key] if self.params[key] in model_options else model_options[0])
            elif key == "DATASET_NAME":
                selected_phase = self.params.get("TRAINING_PHASE", "pretrain")
                new_options = self.dataset_options.get(selected_phase, [])
                entry['values'] = new_options
                entry.set(self.params[key] if self.params[key] in new_options else (new_options[0] if new_options else ""))
            elif key == "OUTPUT_DIR":
                entry.delete(0, tk.END)
                entry.insert(0, self.params[key])
                entry.config(background='white')
            elif key in ["MODEL_URL", "DATASET_URL"]:
                entry.delete(0, tk.END)
                entry.put_placeholder()
                entry.config(background='white')
            elif key in ["TP", "PP"]:
                entry.delete(0, tk.END)
                entry.config(background='white')
            elif key == "VERSION":
                entry.delete(0, tk.END)
                entry.insert(0, self.params[key])
                entry.config(background='white')  # 恢复背景色
            else:
                entry.delete(0, tk.END)
                entry.insert(0, self.params[key])

        # 重置sh_file并禁用“复制”按钮
        self.sh_file = None
        self.copy_button.config(state='disabled')

        self.log_message("参数已重置到初始值")
        messagebox.showinfo("重置成功", "所有参数已重置到初始值")

    def log_message(self, message):
        """在日志区域添加一条消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # 自动滚动到最后
        self.log_text.config(state='disabled')

    def generate_parameter(self, aiak_job_config_str=None):
        """生成AIHC参数并记录日志"""
        self.log_message(f'开始生成AIHC参数...{aiak_job_config_str}')

        try:
            # 从参数中获取用户选择的目录
            chain_job_config = self.params.get("OUTPUT_DIR", "")
            if not chain_job_config:
                raise ValueError("未选择 OUTPUT_DIR 目录")

            job_chain_info = generate_aiak_parameter(chain_job_config, aiak_job_config_str)
            # 记录生成的AIHC参数
            self.log_message("生成的AIHC参数：")
            self.log_message(json.dumps(job_chain_info, indent=4))
            self.sh_file = job_chain_info.get('one_job_command_config')

            if self.sh_file and os.path.isfile(self.sh_file):
                self.log_message(f"脚本文件已生成：{self.sh_file}")
                self.copy_button.config(state='normal')
            else:
                self.log_message("脚本文件未生成或路径无效")
                self.copy_button.config(state='disabled')

        except Exception as e:
            self.log_message(f"生成AIHC参数时发生错误：{e}")
            messagebox.showerror("错误", f"生成AIHC参数时发生错误：{e}")

    def copy_sh_file(self):
        """复制生成的脚本文件内容到剪贴板"""
        if self.sh_file and os.path.isfile(self.sh_file):
            try:
                with open(self.sh_file, 'r') as file:
                    content = file.read()
                pyperclip.copy(content)
                self.log_message("脚本文件内容已复制到剪贴板")
                messagebox.showinfo("复制成功", "脚本文件内容已复制到剪贴板")
            except Exception as e:
                self.log_message(f"复制脚本文件时发生错误：{e}")
                messagebox.showerror("错误", f"复制脚本文件时发生错误：{e}")
        else:
            self.log_message("脚本文件不存在，无法复制")
            messagebox.showerror("错误", "脚本文件不存在，无法复制")


def main():
    root = tk.Tk()
    ParameterConfigApp(root, input_params)
    root.mainloop()


if __name__ == "__main__":
    main()
