import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict
from parser.parser_factory import ParserFactory
from exporter.exporter import Exporter
from ui.variable_table import VariableTable
from ui.variable_dialog import VariableDialog
from ui.batch_edit_dialog import BatchEditDialog

class MainWindow:
    """
    主窗口类
    
    应用程序的主界面，包含菜单、工具栏和变量表格
    """
    
    def __init__(self, root):
        """
        初始化主窗口
        
        参数:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("PLC变量表解析工具")
        self.root.geometry("800x600")
        
        self.variables: List[Dict] = []
        self.parser_factory = ParserFactory()
        self.exporter = Exporter()
        self.original_fieldnames = None
        self.original_encoding = None
        self.is_work3_format = False
        
        # 创建菜单
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建变量表格
        self.create_variable_table()
    
    def create_menu(self):
        """
        创建菜单
        """
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="导出", command=self.export_file, accelerator="Ctrl+E")
        file_menu.add_command(label="解析接口文档", command=self.parse_intdoc, accelerator="Ctrl+I")
        file_menu.add_command(label="创建空文件", command=self.create_empty_file)
        file_menu.add_command(label="转换文件", command=self.convert_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="添加变量", command=self.add_variable, accelerator="Ctrl+N")
        edit_menu.add_command(label="编辑变量", command=self.edit_variable, accelerator="Ctrl+M")
        edit_menu.add_command(label="批量编辑", command=self.batch_edit_variables, accelerator="Ctrl+B")
        edit_menu.add_command(label="删除变量", command=self.delete_variable, accelerator="Delete")
        menubar.add_cascade(label="编辑", menu=edit_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # 绑定快捷键
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-e>", lambda e: self.export_file())
        self.root.bind("<Control-i>", lambda e: self.parse_intdoc())
        self.root.bind("<Control-n>", lambda e: self.add_variable())
        self.root.bind("<Control-m>", lambda e: self.edit_variable())
        self.root.bind("<Control-b>", lambda e: self.batch_edit_variables())
        self.root.bind("<Delete>", lambda e: self.delete_variable())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
    
    def create_toolbar(self):
        """
        创建工具栏
        """
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # 打开按钮
        open_button = ttk.Button(toolbar, text="打开", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5)
        
        # 导出按钮
        export_button = ttk.Button(toolbar, text="导出", command=self.export_file)
        export_button.pack(side=tk.LEFT, padx=5)
        
        # 解析接口文档按钮
        intdoc_button = ttk.Button(toolbar, text="解析接口文档", command=self.parse_intdoc)
        intdoc_button.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        separator = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 添加变量按钮
        add_button = ttk.Button(toolbar, text="添加", command=self.add_variable)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 编辑变量按钮
        edit_button = ttk.Button(toolbar, text="编辑", command=self.edit_variable)
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # 批量编辑按钮
        batch_edit_button = ttk.Button(toolbar, text="批量编辑", command=self.batch_edit_variables)
        batch_edit_button.pack(side=tk.LEFT, padx=5)
        
        # 删除变量按钮
        delete_button = ttk.Button(toolbar, text="删除", command=self.delete_variable)
        delete_button.pack(side=tk.LEFT, padx=5)
    
    def create_variable_table(self):
        """
        创建变量表格
        """
        self.variable_table = VariableTable(self.root, self.variables)
        self.variable_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def open_file(self):
        """
        打开文件
        """
        file_path = filedialog.askopenfilename(
            title="选择变量表文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        # 询问用户选择PLC格式
        plc_format = self.ask_plc_format()
        if not plc_format:
            return
        
        # 保存原始文件的字段名和编码，用于导出时保持格式一致
        try:
            from utils.encoding_detector import EncodingDetector
            encoding_detector = EncodingDetector()
            self.original_encoding = encoding_detector.detect_encoding(file_path)
            
            # 读取文件内容，判断是否是Work3格式
            self.is_work3_format = False
            with open(file_path, 'r', encoding=self.original_encoding) as f:
                lines = f.readlines()
                if lines and 'FX5U&RCPU模板_AI测试' in lines[0]:
                    self.is_work3_format = True
            
            # 读取字段名
            with open(file_path, 'r', encoding=self.original_encoding, newline='') as f:
                import csv
                reader = csv.DictReader(f)
                self.original_fieldnames = reader.fieldnames
        except Exception as e:
            print(f"读取原始文件格式失败: {e}")
            # 即使读取失败，也尝试解析文件
            self.original_fieldnames = None
            # 但仍然保持原始编码
            try:
                from utils.encoding_detector import EncodingDetector
                encoding_detector = EncodingDetector()
                self.original_encoding = encoding_detector.detect_encoding(file_path)
            except:
                self.original_encoding = None
        
        # 创建解析器并解析文件
        parser = self.parser_factory.create_parser(plc_format, file_path)
        if parser:
            try:
                self.variables = parser.parse()
                self.variable_table.update_table(self.variables)
                messagebox.showinfo("成功", f"解析成功，共{len(self.variables)}个变量")
            except Exception as e:
                messagebox.showerror("错误", f"解析失败: {str(e)}")
        else:
            messagebox.showerror("错误", "不支持的PLC格式")
    
    def ask_plc_format(self):
        """
        询问用户选择PLC格式
        
        返回:
            str: 选择的PLC格式
        """
        format_window = tk.Toplevel(self.root)
        format_window.title("选择PLC格式")
        format_window.geometry("300x200")
        format_window.transient(self.root)
        format_window.grab_set()
        
        selected_format = tk.StringVar()
        
        tk.Label(format_window, text="请选择PLC软件格式:").pack(pady=10)
        
        formats = self.parser_factory.get_supported_formats()
        for fmt in formats:
            tk.Radiobutton(
                format_window,
                text=fmt.capitalize(),
                variable=selected_format,
                value=fmt
            ).pack(anchor=tk.W, padx=20)
        
        result = None
        
        def confirm():
            nonlocal result
            result = selected_format.get()
            format_window.destroy()
        
        def cancel():
            nonlocal result
            result = None
            format_window.destroy()
        
        btn_frame = tk.Frame(format_window)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="确定", command=confirm).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=cancel).pack(side=tk.LEFT, padx=10)
        
        self.root.wait_window(format_window)
        return result
    
    def parse_intdoc(self):
        """
        解析接口文档(INT.md)并自动导出Excel到同文件夹

        流程：
            1. 弹出文件选择对话框（.md过滤器）
            2. 调用IntDocParser解析变量+结构体字段
            3. 构造导出路径：INT.md所在目录/原文件名_变量表.xlsx
            4. 调用Exporter.export_to_excel导出多Sheet Excel
            5. 刷新主表格显示变量
            6. 弹出成功对话框（含变量数/结构体字段数/导出路径）

        异常处理：
            - 用户取消选择：静默返回
            - 解析失败：弹错误框
            - 导出失败：弹错误框但变量已加载到表格
            - 解析后变量为空：弹警告框
        """
        # 选择接口文档文件
        file_path = filedialog.askopenfilename(
            title="选择接口文档(INT.md)",
            filetypes=[("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )

        if not file_path:
            return

        # 创建解析器并解析
        parser = self.parser_factory.create_parser('intdoc', file_path)
        if not parser:
            messagebox.showerror("错误", "创建接口文档解析器失败")
            return

        try:
            variables = parser.parse()
            struct_fields = parser.get_struct_fields()
        except Exception as e:
            messagebox.showerror("错误", f"解析接口文档失败: {str(e)}")
            return

        # 检查解析结果
        if not variables:
            messagebox.showwarning(
                "警告",
                "解析完成但未提取到变量，请确认文件是接口文档(INT.md)格式"
            )
            return

        # 构造导出路径：INT.md所在目录 + 原文件名_变量表.xlsx
        file_dir = os.path.dirname(file_path)
        file_basename = os.path.basename(file_path)
        file_stem = os.path.splitext(file_basename)[0]
        output_filename = f"{file_stem}_变量表.xlsx"
        output_path = os.path.join(file_dir, output_filename)

        # 导出Excel
        export_success = self.exporter.export_to_excel(
            variables, output_path, struct_fields=struct_fields
        )

        # 更新主表格状态（重置CSV相关状态，避免后续导出误用Work3格式）
        self.variables = variables
        self.original_fieldnames = None
        self.original_encoding = None
        self.is_work3_format = False
        self.variable_table.update_table(self.variables)

        # 反馈结果
        if export_success:
            messagebox.showinfo(
                "成功",
                f"接口文档解析完成\n"
                f"• 变量数：{len(variables)}\n"
                f"• 结构体字段数：{len(struct_fields)}\n"
                f"• Excel已导出至：{output_path}"
            )
        else:
            messagebox.showerror(
                "错误",
                f"Excel导出失败，但变量已加载到表格（共{len(variables)}个）\n"
                f"可使用\"导出\"按钮手动导出其他格式"
            )

    def export_file(self):
        """
        导出文件
        """
        if not self.variables:
            messagebox.showwarning("警告", "没有变量可导出")
            return
        
        # 询问用户选择导出格式
        format_window = tk.Toplevel(self.root)
        format_window.title("选择导出格式")
        format_window.geometry("300x200")
        format_window.transient(self.root)
        format_window.grab_set()
        
        selected_format = tk.StringVar(value="csv")
        
        tk.Label(format_window, text="请选择导出格式:").pack(pady=10)
        
        tk.Radiobutton(
            format_window,
            text="CSV",
            variable=selected_format,
            value="csv"
        ).pack(anchor=tk.W, padx=20)
        
        tk.Radiobutton(
            format_window,
            text="JSON",
            variable=selected_format,
            value="json"
        ).pack(anchor=tk.W, padx=20)
        
        result = None
        
        def confirm():
            nonlocal result
            result = selected_format.get()
            format_window.destroy()
        
        def cancel():
            nonlocal result
            result = None
            format_window.destroy()
        
        btn_frame = tk.Frame(format_window)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="确定", command=confirm).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=cancel).pack(side=tk.LEFT, padx=10)
        
        self.root.wait_window(format_window)
        
        if not result:
            return
        
        # 选择导出路径
        file_ext = ".csv" if result == "csv" else ".json"
        output_path = filedialog.asksaveasfilename(
            title="保存导出文件",
            defaultextension=file_ext,
            filetypes=[(f"{result.upper()}文件", f"*{file_ext}"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
        
        # 执行导出
        # 如果是CSV格式，使用与原始文件相同的格式
        if result == "csv" and hasattr(self, 'is_work3_format') and self.is_work3_format:
            # Work3格式，直接调用export_to_work3_format
            encoding = self.original_encoding if hasattr(self, 'original_encoding') and self.original_encoding is not None else 'utf-16'
            success = self.exporter.export_to_work3_format(self.variables, output_path, encoding)
        elif result == "csv" and hasattr(self, 'original_fieldnames') and self.original_fieldnames:
            # 普通CSV格式，映射通用格式到原始格式
            mapped_variables = []
            for var in self.variables:
                mapped = {}
                for field in self.original_fieldnames:
                    if field == '序号':
                        mapped[field] = ''
                    elif field == '类别':
                        mapped[field] = var.get('scope', '')
                    elif field == '名称':
                        mapped[field] = var.get('name', '')
                    elif field == '数据类型':
                        mapped[field] = var.get('type', '')
                    elif field == '隐藏初始值':
                        mapped[field] = ''
                    elif field == '初始值':
                        mapped[field] = ''
                    elif field == '掉电保持':
                        mapped[field] = ''
                    elif field == '注释':
                        mapped[field] = var.get('description', '')
                    elif field == '类型':
                        mapped[field] = var.get('scope', '')
                    elif field == '变量名':
                        mapped[field] = var.get('name', '')
                    elif field == '默认值':
                        mapped[field] = ''
                    elif field == '变量组':
                        mapped[field] = ''
                    elif field == '隐含初始值':
                        mapped[field] = ''
                    else:
                        mapped[field] = var.get(field, '')
                mapped_variables.append(mapped)
            # 使用原始文件的编码
            encoding = self.original_encoding if hasattr(self, 'original_encoding') and self.original_encoding is not None else 'utf-8'
            success = self.exporter.export_to_csv(mapped_variables, output_path, encoding, self.original_fieldnames)
        else:
            success = self.exporter.export_to_format(self.variables, output_path, result)
        if success:
            messagebox.showinfo("成功", f"导出成功: {output_path}")
        else:
            messagebox.showerror("错误", "导出失败")
    
    def add_variable(self):
        """
        添加变量
        """
        dialog = VariableDialog(self.root, title="添加变量")
        variable = dialog.show()
        
        if variable:
            self.variables.append(variable)
            self.variable_table.update_table(self.variables)
    
    def edit_variable(self):
        """
        编辑变量
        """
        selected_index = self.variable_table.get_selected_index()
        if selected_index == -1:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        
        variable = self.variables[selected_index]
        dialog = VariableDialog(self.root, title="编辑变量", variable=variable)
        updated_variable = dialog.show()
        
        if updated_variable:
            self.variables[selected_index] = updated_variable
            self.variable_table.update_table(self.variables)
    
    def delete_variable(self):
        """
        删除变量
        """
        selected_index = self.variable_table.get_selected_index()
        if selected_index == -1:
            messagebox.showwarning("警告", "请先选择一个变量")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的变量吗？"):
            self.variables.pop(selected_index)
            self.variable_table.update_table(self.variables)
    
    def batch_edit_variables(self):
        """
        批量编辑变量
        """
        selected_indices = self.variable_table.get_selected_indices()
        if not selected_indices:
            messagebox.showwarning("警告", "请先选择要编辑的变量")
            return
        
        # 创建批量编辑对话框
        dialog = BatchEditDialog(self.root, len(selected_indices))
        changes = dialog.show()
        
        if changes:
            # 应用更改到选中的变量
            for index in selected_indices:
                if 0 <= index < len(self.variables):
                    variable = self.variables[index]
                    for field, value in changes.items():
                        if value:
                            variable[field] = value
            
            self.variable_table.update_table(self.variables)
            messagebox.showinfo("成功", f"已批量编辑{len(selected_indices)}个变量")
    
    def show_about(self):
        """
        显示关于对话框
        """
        messagebox.showinfo(
            "关于",
            "PLC变量表解析工具 v1.1.0\n\n"+
            "用于解析和管理不同PLC软件系统的变量表\n\n"+
            "支持格式: Autoshop, Work3, Codesys, SCL, 接口文档(INT.md)\n\n"+
            "快捷键: Ctrl+O打开 Ctrl+E导出 Ctrl+I解析接口文档"
        )
    
    def create_empty_file(self):
        """
        创建与源文件格式和编码相同的空文件
        """
        # 选择源文件
        source_path = filedialog.askopenfilename(
            title="选择源CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not source_path:
            return
        
        # 选择输出路径
        output_path = filedialog.asksaveasfilename(
            title="保存空文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
        
        # 执行创建
        try:
            success = self.exporter.create_empty_file(source_path, output_path)
            if success:
                messagebox.showinfo("成功", f"创建空文件成功: {output_path}")
            else:
                messagebox.showerror("错误", "创建空文件失败")
        except Exception as e:
            messagebox.showerror("错误", f"创建空文件失败: {str(e)}")
    
    def convert_file(self):
        """
        将目标文件转换为与源文件相同格式和编码的文件
        """
        # 选择源文件（格式参考）
        source_path = filedialog.askopenfilename(
            title="选择源CSV文件（格式参考）",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not source_path:
            return
        
        # 选择目标文件（待转换）
        target_path = filedialog.askopenfilename(
            title="选择目标CSV文件（待转换）",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not target_path:
            return
        
        # 选择输出路径
        output_path = filedialog.asksaveasfilename(
            title="保存转换后的文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if not output_path:
            return
        
        # 执行转换
        try:
            success = self.exporter.convert_file(source_path, target_path, output_path)
            if success:
                messagebox.showinfo("成功", f"转换成功: {output_path}")
            else:
                messagebox.showerror("错误", "转换失败")
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")