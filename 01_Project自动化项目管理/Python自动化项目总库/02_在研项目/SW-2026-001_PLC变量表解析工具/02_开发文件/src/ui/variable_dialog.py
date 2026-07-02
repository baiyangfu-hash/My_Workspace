#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量对话框

用于添加和编辑变量的对话框
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional


class VariableDialog:
    """
    变量对话框类
    
    用于添加和编辑变量的对话框
    """
    
    def __init__(self, parent, title: str = "变量编辑", variable: Optional[Dict] = None):
        """
        初始化变量对话框
        
        参数:
            parent: 父窗口
            title (str): 对话框标题
            variable (Optional[Dict]): 待编辑的变量，如果为None则为添加模式
        """
        self.parent = parent
        self.title = title
        self.variable = variable or {}
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def show(self) -> Optional[Dict]:
        """
        显示对话框
        
        返回:
            Optional[Dict]: 用户输入的变量信息，如果取消则返回None
        """
        # 创建界面
        self.create_widgets()
        
        # 显示对话框并等待用户操作
        self.dialog.wait_window()
        
        return self.result
    
    def create_widgets(self):
        """
        创建对话框界面
        """
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入字段
        fields = [
            ("变量名", "name"),
            ("数据类型", "type"),
            ("地址", "address"),
            ("注释", "description"),
            ("作用域", "scope")
        ]
        
        self.entries = {}
        
        for label_text, field_name in fields:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(frame, text=label_text, width=10)
            label.pack(side=tk.LEFT, padx=5)
            
            if field_name == 'type':
                # 为数据类型添加下拉菜单
                combobox = ttk.Combobox(frame, values=[
                    'BOOL', 'BYTE', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 
                    'STRING', 'TIME', 'TOD', 'DATE', 'DT', 'TON', 'TOF', 'TP'
                ])
                combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                # 填充现有值
                if field_name in self.variable:
                    combobox.set(self.variable[field_name])
                self.entries[field_name] = combobox
            else:
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                # 填充现有值
                if field_name in self.variable:
                    entry.insert(0, self.variable[field_name])
                self.entries[field_name] = entry
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="确定", command=self.on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def on_ok(self):
        """
        处理确定按钮点击
        """
        # 收集用户输入
        self.result = {
            'name': self.entries['name'].get().strip(),
            'type': self.entries['type'].get().strip(),
            'address': self.entries['address'].get().strip(),
            'description': self.entries['description'].get().strip(),
            'scope': self.entries['scope'].get().strip()
        }
        
        # 验证输入
        if not self.result['name']:
            self.show_error("变量名不能为空")
            return
        
        # 关闭对话框
        self.dialog.destroy()
    
    def on_cancel(self):
        """
        处理取消按钮点击
        """
        self.result = None
        self.dialog.destroy()
    
    def show_error(self, message: str):
        """
        显示错误信息
        
        参数:
            message (str): 错误信息
        """
        error_dialog = tk.Toplevel(self.dialog)
        error_dialog.title("错误")
        error_dialog.geometry("300x100")
        error_dialog.transient(self.dialog)
        error_dialog.grab_set()
        
        label = ttk.Label(error_dialog, text=message, padding="20")
        label.pack(fill=tk.BOTH, expand=True)
        
        button = ttk.Button(error_dialog, text="确定", command=error_dialog.destroy)
        button.pack(pady=10)
        
        error_dialog.wait_window()
