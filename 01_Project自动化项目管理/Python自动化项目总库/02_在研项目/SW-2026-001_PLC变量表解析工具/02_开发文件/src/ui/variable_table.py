#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量表格

用于显示和管理变量列表的表格界面
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict


class VariableTable(tk.Frame):
    """
    变量表格类
    
    用于显示和管理变量列表的表格界面
    """
    
    def __init__(self, parent, variables: List[Dict]):
        """
        初始化变量表格
        
        参数:
            parent: 父窗口
            variables (List[Dict]): 变量列表
        """
        super().__init__(parent)
        
        self.variables = variables
        self.selected_index = -1
        
        # 创建表格
        self.create_table()
    
    def create_table(self):
        """
        创建表格
        """
        # 创建滚动条
        scrollbar_y = tk.Scrollbar(self, orient=tk.VERTICAL)
        scrollbar_x = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        
        # 创建表格
        self.tree = ttk.Treeview(
            self,
            columns=('name', 'type', 'address', 'description', 'scope'),
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # 设置列属性
        self.tree.column('name', width=150, anchor=tk.W)
        self.tree.column('type', width=100, anchor=tk.W)
        self.tree.column('address', width=150, anchor=tk.W)
        self.tree.column('description', width=200, anchor=tk.W)
        self.tree.column('scope', width=100, anchor=tk.W)
        
        # 设置列标题
        self.tree.heading('name', text='变量名')
        self.tree.heading('type', text='数据类型')
        self.tree.heading('address', text='地址')
        self.tree.heading('description', text='注释')
        self.tree.heading('scope', text='作用域')
        
        # 绑定事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # 放置滚动条
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x.config(command=self.tree.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 放置表格
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 初始填充表格
        self.update_table(self.variables)
    
    def update_table(self, variables: List[Dict]):
        """
        更新表格数据
        
        参数:
            variables (List[Dict]): 新的变量列表
        """
        self.variables = variables
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充表格
        for i, var in enumerate(variables):
            self.tree.insert(
                '',
                tk.END,
                iid=i,
                values=(
                    var.get('name', ''),
                    var.get('type', ''),
                    var.get('address', ''),
                    var.get('description', ''),
                    var.get('scope', '')
                )
            )
        
        # 重置选中索引
        self.selected_index = -1
    
    def on_select(self, event):
        """
        处理选择事件
        
        参数:
            event: 事件对象
        """
        selected_items = self.tree.selection()
        if selected_items:
            self.selected_index = int(selected_items[0])
        else:
            self.selected_index = -1
    
    def get_selected_index(self):
        """
        获取当前选中的索引
        
        返回:
            int: 选中的索引，-1表示未选中
        """
        return self.selected_index
    
    def get_selected_indices(self):
        """
        获取所有选中的索引
        
        返回:
            List[int]: 选中的索引列表，空列表表示未选中
        """
        selected_items = self.tree.selection()
        return [int(item) for item in selected_items]
    
    def get_selected_variable(self):
        """
        获取当前选中的变量
        
        返回:
            Dict: 选中的变量，None表示未选中
        """
        if 0 <= self.selected_index < len(self.variables):
            return self.variables[self.selected_index]
        return None
