#!/usr/bin/env python3
# coding=utf-8

import sys
import os
import json
import re
import pyperclip
from datetime import datetime
from itertools import zip_longest
from functools import partial

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QRadioButton, QButtonGroup, QFileDialog,
    QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTextEdit, QGroupBox, QScrollArea, QSizePolicy
)
from PySide6.QtGui import QIntValidator, QFont, QColor, QTextCursor
from PySide6.QtCore import Qt

from baidubce.services.aihc.aihc_client import generate_aiak_parameter  # Ensure this is installed


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


class PlaceholderLineEdit(QLineEdit):
    """QLineEdit widget with placeholder functionality."""

    def __init__(self, placeholder="", color=QColor('grey'), parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_palette = self.palette()
        self.setPlaceholderText(self.placeholder)

        # Optional: Additional styling or behavior can be added here if needed


class ParameterConfigApp(QWidget):
    def __init__(self, params):
        super().__init__()
        self.sh_file = None  # 用于存储生成的脚本文件路径
        self.setWindowTitle("参数配置")
        self.params = params.copy()  # 保留初始参数
        self.entries = {}  # 存储每个参数对应的组件

        # 设置窗口大小和最小尺寸
        self.resize(1000, 800)
        self.setMinimumSize(800, 700)

        # 主布局
        main_layout = QVBoxLayout(self)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        # 主框架
        main_frame = QWidget()
        scroll.setWidget(main_frame)

        grid = QGridLayout(main_frame)
        grid.setSpacing(10)
        main_frame.setLayout(grid)

        # 设置每列的伸缩因子为相同的值，确保三列等宽
        for i in range(6):
            grid.setColumnStretch(i, 1)

        # 定义TRAINING_PHASE与对应的DATASET_NAME选项
        self.training_phase_options = ["pretrain", "sft"]
        self.dataset_options = {
            "pretrain": ["pile_llama_test", "WuDaoCorpus2.0_base_sample"],
            "sft": ["alpaca_zh-llama3-train", "alpaca_zh-llama3-valid"]
        }

        # 动态创建标签和输入组件，每行3个参数（排除 OUTPUT_DIR）
        params_list = list(self.params.items())
        params_list = [item for item in params_list if item[0] != "OUTPUT_DIR"]

        row_num = 0
        for param_group in grouper(params_list, 3):
            for col, (key, value) in enumerate(param_group):
                if key is None:
                    continue  # 如果参数不足3的倍数，跳过

                # 计算实际的列位置
                label_col = col * 2
                entry_col = col * 2 + 1

                # 检查是否为必填项
                is_required = key in required_fields

                # 标签
                label = QLabel(f"{key}{' *' if is_required else ''}")
                font = QFont("Helvetica", 12, QFont.Bold)
                label.setFont(font)
                if is_required:
                    label.setStyleSheet("color: red;")
                grid.addWidget(label, row_num, label_col, alignment=Qt.AlignLeft)

                # 根据key创建不同类型的输入组件
                if key == "TRAINING_PHASE":
                    # 单选按钮
                    training_phase_group = QButtonGroup(self)
                    h_layout = QHBoxLayout()
                    frame = QWidget()
                    frame.setLayout(h_layout)

                    current_phase = self.params[key]
                    for phase in self.training_phase_options:
                        rb = QRadioButton(phase.capitalize())
                        if phase == current_phase:
                            rb.setChecked(True)
                        training_phase_group.addButton(rb)
                        h_layout.addWidget(rb)

                    training_phase_group.buttonClicked.connect(self.update_dataset_options)
                    self.entries[key] = training_phase_group
                    grid.addWidget(frame, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key == "REPLICAS":
                    # 数字输入，限制为整数 >=1
                    entry = QLineEdit()
                    entry.setValidator(QIntValidator(1, 1000000))
                    entry.setText(value)
                    entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = entry
                    grid.addWidget(entry, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key == "MODEL_NAME":
                    # 下拉选项
                    combobox = QComboBox()
                    combobox.addItems(model_options)
                    if value in model_options:
                        combobox.setCurrentText(value)
                    else:
                        combobox.setCurrentText(model_options[0])
                    combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = combobox
                    grid.addWidget(combobox, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key == "DATASET_NAME":
                    # 下拉选项，根据TRAINING_PHASE动态变化
                    combobox = QComboBox()
                    current_phase = self.params.get("TRAINING_PHASE", "pretrain")
                    combobox.addItems(self.dataset_options.get(current_phase, []))
                    if value in [combobox.itemText(i) for i in range(combobox.count())]:
                        combobox.setCurrentText(value)
                    elif combobox.count() > 0:
                        combobox.setCurrentText(combobox.itemText(0))
                    self.entries[key] = combobox
                    combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    grid.addWidget(combobox, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key in ["TP", "PP"]:
                    # 数字输入，限制为正整数
                    entry = QLineEdit()
                    entry.setValidator(QIntValidator(1, 1000000))
                    entry.setText(value)
                    entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = entry
                    grid.addWidget(entry, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key in ["MODEL_URL", "DATASET_URL"]:
                    # 文本输入，必须以bos:/开头（选填）
                    entry = PlaceholderLineEdit("以 bos:/ 开头")
                    entry.setText(value)
                    entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = entry
                    grid.addWidget(entry, row_num, entry_col, alignment=Qt.AlignLeft)

                elif key == "VERSION":
                    # 默认文本输入框，带有特定校验
                    entry = QLineEdit()
                    entry.setMaxLength(30)
                    # 使用 lambda 绑定 key，避免 partial 可能的问题
                    entry.textChanged.connect(lambda text, k=key: self.validate_version(text, k))
                    entry.setText(value)
                    entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = entry
                    print(f"Added {key} to entries")  # 调试信息
                    grid.addWidget(entry, row_num, entry_col, alignment=Qt.AlignLeft)

                else:
                    # 默认文本输入框
                    entry = QLineEdit()
                    entry.setText(value)
                    entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.entries[key] = entry
                    grid.addWidget(entry, row_num, entry_col, alignment=Qt.AlignLeft)

            row_num += 1

        # 单独添加 OUTPUT_DIR 一行
        output_dir_key = "OUTPUT_DIR"
        value = self.params.get(output_dir_key, "")
        is_required = output_dir_key in required_fields

        # 标签
        label = QLabel(f"{output_dir_key}{' *' if is_required else ''}")
        font = QFont("Helvetica", 12, QFont.Bold)
        label.setFont(font)
        if is_required:
            label.setStyleSheet("color: red;")
        grid.addWidget(label, row_num, 0, alignment=Qt.AlignLeft)

        # 目录选择，包含文本框和浏览按钮
        h_layout = QHBoxLayout()

        entry = QLineEdit()
        entry.setText(value)
        entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # 优化点
        self.entries[output_dir_key] = entry
        h_layout.addWidget(entry)

        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(partial(self.browse_directory, entry))
        h_layout.addWidget(browse_button)

        container = QWidget()
        container.setLayout(h_layout)
        grid.addWidget(container, row_num, 1, alignment=Qt.AlignLeft)

        row_num += 1  # 增加行号，为按钮框架和日志区域腾出位置

        # 按钮框架
        button_layout = QHBoxLayout()

        # 生成按钮
        generate_button = QPushButton("生成命令")
        generate_button.clicked.connect(self.save_params)
        button_layout.addWidget(generate_button)

        # 重置按钮
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self.reset_params)
        button_layout.addWidget(reset_button)

        # 复制按钮
        self.copy_button = QPushButton("复制到剪切板")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_sh_file)
        button_layout.addWidget(self.copy_button)

        # 将按钮布局添加到主布局
        grid.addLayout(button_layout, row_num, 0, 1, 6, alignment=Qt.AlignCenter)

        row_num += 1  # 增加行号，为日志区域腾出位置

        # 日志区域
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 10))
        log_layout.addWidget(self.log_text)

        grid.addWidget(log_group, row_num, 0, 1, 6)

        # 初始化 DATASET_NAME 选项
        self.update_dataset_options()

    def browse_directory(self, entry_widget):
        """打开目录选择对话框并设置选定的目录到对应的Entry中"""
        selected_dir = QFileDialog.getExistingDirectory(self, "选择目录", "")
        if selected_dir:
            entry_widget.setText(selected_dir)
            self.log_message(f"选择的目录: {selected_dir}")

    def update_dataset_options(self):
        """根据TRAINING_PHASE更新DATASET_NAME的选项"""
        selected_phase = None
        training_group = self.entries.get("TRAINING_PHASE")
        if training_group:
            for button in training_group.buttons():
                if button.isChecked():
                    selected_phase = button.text().lower()
                    break

        if selected_phase:
            dataset_combobox = self.entries.get("DATASET_NAME")
            if dataset_combobox:
                dataset_combobox.clear()
                new_options = self.dataset_options.get(selected_phase, [])
                dataset_combobox.addItems(new_options)
                # 如果当前选中的值不在新的选项中，则重置
                current_value = self.params.get("DATASET_NAME", "")
                if current_value in new_options:
                    dataset_combobox.setCurrentText(current_value)
                elif new_options:
                    dataset_combobox.setCurrentText(new_options[0])
                else:
                    dataset_combobox.setCurrentText("")
                self.log_message(f"TRAINING_PHASE 改变为 {selected_phase}，更新 DATASET_NAME 选项为: {new_options}")

    def validate_positive_integer(self, text):
        """验证输入是否为正整数"""
        if text == "":
            return True  # 允许清空，由必填项校验处理
        if text.isdigit() and int(text) > 0:
            return True
        else:
            self.beep()
            return False

    def validate_version(self, text, key):
        """验证VERSION输入，只允许小写字母、数字和连字符，长度1-30，结尾必须是小写字母或数字"""
        pattern = re.compile(r'^[a-z0-9]([a-z0-9\-]{0,28}[a-z0-9])?$')
        if text == "" or pattern.match(text):
            self.entries[key].setStyleSheet("background-color: white;")
        else:
            self.entries[key].setStyleSheet("background-color: pink;")
            self.beep()

    def beep(self):
        """发出提示音"""
        QApplication.beep()

    def log_message(self, message):
        """在日志区域添加一条消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        self.log_text.moveCursor(QTextCursor.End)  # 自动滚动到最后

    def validate_inputs(self):
        """验证所有输入字段并返回错误信息列表"""
        updated_params = {}
        missing_fields = []
        invalid_fields = []

        # Collect inputs
        for key, widget in self.entries.items():
            if key == "TRAINING_PHASE":
                selected_phase = None
                for button in widget.buttons():
                    if button.isChecked():
                        selected_phase = button.text().lower()
                        break
                updated_params[key] = selected_phase if selected_phase else ""
            elif key == "OUTPUT_DIR":
                updated_params[key] = widget.text().strip()
            elif key in ["REPLICAS", "TP", "PP"]:
                updated_params[key] = widget.text().strip()
            elif key in ["MODEL_URL", "DATASET_URL"]:
                updated_params[key] = widget.text().strip()
            elif key == "VERSION":
                updated_params[key] = widget.text().strip()
            else:
                updated_params[key] = widget.currentText() if isinstance(widget, QComboBox) else widget.text().strip()

        # 检查必填项是否填写
        for field in required_fields:
            value = updated_params.get(field, "")
            if not value or (field in ["MODEL_URL", "DATASET_URL"] and value == "以 bos:/ 开头"):
                missing_fields.append(field)

        # 检查特定字段的格式
        # VERSION 字段
        version = updated_params.get("VERSION", "")
        version_pattern = re.compile(r'^[a-z0-9]([a-z0-9\-]{0,28}[a-z0-9])?$')
        if version and not version_pattern.match(version):
            invalid_fields.append("VERSION")

        # TP 和 PP 必须为正整数（如果有输入）
        for field in ["TP", "PP"]:
            value = updated_params.get(field, "")
            if value and (not value.isdigit() or int(value) <= 0):
                invalid_fields.append(field)

        # MODEL_URL 和 DATASET_URL 必须以 bos:/ 开头（如果有输入）
        for field in ["MODEL_URL", "DATASET_URL"]:
            value = updated_params.get(field, "")
            if value and not value.startswith("bos:/") and value != "以 bos:/ 开头":
                invalid_fields.append(field)

        # 检查 OUTPUT_DIR 是否存在且为目录
        chain_job_dir = updated_params.get("OUTPUT_DIR", "")
        if not chain_job_dir:
            missing_fields.append("OUTPUT_DIR")
        elif not os.path.isdir(chain_job_dir):
            invalid_fields.append("OUTPUT_DIR")
            self.log_message(f"OUTPUT_DIR 路径无效或不存在：{chain_job_dir}")

        return updated_params, missing_fields, invalid_fields

    def save_params(self):
        """保存用户输入的参数并记录日志，同时进行必填项和特定字段校验"""
        updated_params, missing_fields, invalid_fields = self.validate_inputs()

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
            QMessageBox.critical(self, "输入错误", full_error_message)
            return

        # 更新内部参数字典
        self.params = updated_params.copy()

        # 处理特殊字段
        self.params['MODEL_URL'] = '' if self.params['MODEL_URL'] == '以 bos:/ 开头' else self.params['MODEL_URL']
        self.params['DATASET_URL'] = '' if self.params['DATASET_URL'] == '以 bos:/ 开头' else self.params['DATASET_URL']

        # 记录日志
        self.log_message("保存参数成功")
        self.log_message(f"更新的参数：{self.params}")

        # 生成AIHC参数
        try:
            aiak_job_config_str = json.dumps(self.params)
            self.generate_parameter(aiak_job_config_str)
        except Exception as e:
            self.log_message(f"生成AIHC参数时发生错误：{e}")
            QMessageBox.critical(self, "错误", f"生成AIHC参数时发生错误：{e}")
            return

        # 如果sh_file已生成，启用“复制”按钮
        if self.sh_file and os.path.isfile(self.sh_file):
            self.copy_button.setEnabled(True)
        else:
            self.copy_button.setEnabled(False)

        # 显示成功消息
        QMessageBox.information(self, "保存成功", "执行命令生成成功，可复制到剪贴板")

    def reset_params(self):
        """重置所有输入框到初始值"""
        for key, widget in self.entries.items():
            if key == "TRAINING_PHASE":
                selected_phase = self.params[key]
                for button in widget.buttons():
                    button.setChecked(button.text().lower() == selected_phase)
            elif key == "MODEL_NAME":
                if self.params[key] in model_options:
                    widget.setCurrentText(self.params[key])
                else:
                    widget.setCurrentText(model_options[0])
            elif key == "DATASET_NAME":
                selected_phase = self.params.get("TRAINING_PHASE", "pretrain")
                new_options = self.dataset_options.get(selected_phase, [])
                widget.clear()
                widget.addItems(new_options)
                if self.params[key] in new_options:
                    widget.setCurrentText(self.params[key])
                elif new_options:
                    widget.setCurrentText(new_options[0])
                else:
                    widget.setCurrentText("")
            elif key == "OUTPUT_DIR":
                widget.setText(self.params[key])
                widget.setStyleSheet("background-color: white;")
            elif key in ["MODEL_URL", "DATASET_URL"]:
                widget.setText(self.params[key] if self.params[key] else "")
                widget.setStyleSheet("background-color: white;")
            elif key in ["TP", "PP"]:
                widget.setText(self.params[key] if self.params[key] else "")
                widget.setStyleSheet("background-color: white;")
            elif key == "VERSION":
                widget.setText(self.params[key] if self.params[key] else "")
                widget.setStyleSheet("background-color: white;")
            else:
                widget.setText(self.params[key] if self.params[key] else "")

        # 重置sh_file并禁用“复制”按钮
        self.sh_file = None
        self.copy_button.setEnabled(False)

        self.log_message("参数已重置到初始值")
        QMessageBox.information(self, "重置成功", "所有参数已重置到初始值")

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
                self.copy_button.setEnabled(True)
            else:
                self.log_message("脚本文件未生成或路径无效")
                self.copy_button.setEnabled(False)

        except Exception as e:
            self.log_message(f"生成AIHC参数时发生错误：{e}")
            QMessageBox.critical(self, "错误", f"生成AIHC参数时发生错误：{e}")

    def copy_sh_file(self):
        """复制生成的脚本文件内容到剪贴板"""
        if self.sh_file and os.path.isfile(self.sh_file):
            try:
                with open(self.sh_file, 'r') as file:
                    content = file.read()
                pyperclip.copy(content)
                self.log_message("脚本文件内容已复制到剪贴板")
                QMessageBox.information(self, "复制成功", "脚本文件内容已复制到剪贴板")
            except Exception as e:
                self.log_message(f"复制脚本文件时发生错误：{e}")
                QMessageBox.critical(self, "错误", f"复制脚本文件时发生错误：{e}")
        else:
            self.log_message("脚本文件不存在，无法复制")
            QMessageBox.critical(self, "错误", "脚本文件不存在，无法复制")


def main():
    app = QApplication(sys.argv)
    window = ParameterConfigApp(input_params)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
