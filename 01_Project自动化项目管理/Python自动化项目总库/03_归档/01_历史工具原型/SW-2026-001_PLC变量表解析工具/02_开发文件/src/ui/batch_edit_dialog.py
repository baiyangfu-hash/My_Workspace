import tkinter as tk
from tkinter import ttk

class BatchEditDialog:
    """
    批量编辑对话框
    
    用于同时编辑多个变量的属性
    """
    
    def __init__(self, parent, variable_count):
        """
        初始化批量编辑对话框
        
        参数:
            parent: 父窗口
            variable_count: 要编辑的变量数量
        """
        self.parent = parent
        self.variable_count = variable_count
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"批量编辑 ({variable_count}个变量)")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def show(self):
        """
        显示对话框
        
        返回:
            dict: 用户输入的更改，如果取消则返回None
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
            ("数据类型", "type"),
            ("地址", "address"),
            ("作用域", "scope")
        ]
        
        self.entries = {}
        
        for label_text, field_name in fields:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(frame, text=label_text, width=10)
            label.pack(side=tk.LEFT, padx=5)
            
            if field_name == 'type':
                combobox = ttk.Combobox(frame, values=[
                    '', 'BOOL', 'BYTE', 'WORD', 'DWORD', 'INT', 'DINT', 'REAL', 
                    'STRING', 'TIME', 'TOD', 'DATE', 'DT', 'TON', 'TOF', 'TP'
                ])
                combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                self.entries[field_name] = combobox
            elif field_name == 'scope':
                combobox = ttk.Combobox(frame, values=[
                    '', 'VAR', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 
                    'VAR_TEMP', 'VAR_STAT', 'VAR_EXTERNAL', 'VAR_GLOBAL', 
                    'VAR_CONFIG', 'CONSTANT'
                ])
                combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                self.entries[field_name] = combobox
            else:
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                self.entries[field_name] = entry
        
        # 提示信息
        hint_frame = ttk.Frame(main_frame)
        hint_frame.pack(fill=tk.X, pady=10)
        hint_label = ttk.Label(hint_frame, text="提示: 留空表示不修改该字段", foreground="gray")
        hint_label.pack(side=tk.LEFT, padx=5)
        
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
            'type': self.entries['type'].get().strip(),
            'address': self.entries['address'].get().strip(),
            'scope': self.entries['scope'].get().strip()
        }
        
        # 关闭对话框
        self.dialog.destroy()
    
    def on_cancel(self):
        """
        处理取消按钮点击
        """
        self.result = None
        self.dialog.destroy()