#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC变量表解析工具

应用程序主入口
"""

import tkinter as tk
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """
    主函数
    
    启动应用程序
    """
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
