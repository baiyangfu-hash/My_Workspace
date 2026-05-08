#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变量导出器

用于将解析后的变量导出到不同格式的文件
"""

import csv
import json
from typing import List, Dict
from utils.file_operator import FileOperator
from utils.encoding_detector import EncodingDetector


class Exporter:
    """
    变量导出器
    
    用于将解析后的变量导出到不同格式的文件
    """
    
    def __init__(self):
        """
        初始化导出器
        """
        self.file_operator = FileOperator()
    
    def export_to_csv(self, variables: List[Dict], output_path: str, encoding: str = 'utf-8', fieldnames: List[str] = None) -> bool:
        """
        导出变量到CSV文件
        
        参数:
            variables (List[Dict]): 变量列表
            output_path (str): 输出文件路径
            encoding (str): 文件编码
            fieldnames (List[str]): 字段名称列表
            
        返回:
            bool: 导出是否成功
        """
        try:
            # 检查是否是Work3格式
            is_work3_format = False
            if fieldnames and len(fieldnames) == 1 and 'FX5U&RCPU模板_AI测试' in fieldnames[0]:
                is_work3_format = True
            
            # 处理Work3格式
            if is_work3_format:
                return self.export_to_work3_format(variables, output_path, encoding)
            
            # 普通CSV格式
            if not fieldnames:
                fieldnames = ['name', 'type', 'address', 'description', 'scope']
            
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for var in variables:
                    # 确保每个变量都有所有字段
                    row = {}
                    for field in fieldnames:
                        row[field] = var.get(field, '')
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"导出CSV失败: {str(e)}")
            return False
    
    def export_to_work3_format(self, variables: List[Dict], output_path: str, encoding: str = 'utf-16') -> bool:
        """
        导出变量到Work3格式文件
        
        参数:
            variables (List[Dict]): 变量列表
            output_path (str): 输出文件路径
            encoding (str): 文件编码
            
        返回:
            bool: 导出是否成功
        """
        try:
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                # 写入第一行（文件名）- 需要引号
                f.write('"FX5U&RCPU模板_AI测试"\n')
                
                # 写入第二行（表头）- 使用制表符分隔
                header = '"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"'
                f.write(header + '\n')
                
                # 写入变量数据
                for var in variables:
                    # 构建Work3格式的行
                    scope = var.get('scope', 'VAR_INPUT')
                    name = var.get('name', '')
                    data_type = var.get('type', 'BOOL')
                    address = var.get('address', '')
                    description = var.get('description', '')
                    
                    # 构建字段 - 使用制表符分隔
                    fields = [
                        f'"{scope}"',  # 1: 类
                        f'"{name}"',  # 2: 标签名
                        f'"{data_type}"',  # 3: 数据类型
                        '""',  # 4: 常数
                        '"FALSE"',  # 5: 初始值
                        '""',  # 6: 分配(软元件/标签)
                        '""',  # 7: 地址
                        f'"{description}"',  # 8: 注释
                        '""',  # 9: 注释2
                        '""',  # 10: 注释3
                        '""',  # 11: 注释4
                        '""',  # 12: 注释5
                        '""',  # 13: Japanese/日本語
                        '""',  # 14: English
                        f'"{description}"',  # 15: Chinese Simplified/简体中文
                        '""',  # 16: Korean/한국어
                        '""',  # 17: Chinese Traditional/繁體中文
                        '""',  # 18: German/Deutsch
                        '""',  # 19: Italian/Italiano
                        '""',  # 20: Reserved1
                        '""',  # 21: Reserved2
                        '""',  # 22: Reserved3
                        '""',  # 23: Reserved4
                        '""',  # 24: 备注
                        '""',  # 25: 系统标签的关联
                        '""',  # 26: 系统标签名
                        '""',  # 27: 属性
                    ]
                    
                    # 组合成行并写入 - 使用制表符分隔
                    row = '\t'.join(fields)
                    f.write(row + '\n')
            
            return True
        except Exception as e:
            print(f"导出Work3格式失败: {str(e)}")
            return False
    
    def create_empty_file(self, source_path: str, output_path: str) -> bool:
        """
        创建与源文件格式和编码相同的空文件
        
        参数:
            source_path (str): 源文件路径
            output_path (str): 输出文件路径
            
        返回:
            bool: 创建是否成功
        """
        try:
            # 检测源文件编码
            encoding_detector = EncodingDetector()
            encoding = encoding_detector.detect_encoding(source_path)
            
            # 读取源文件内容，判断是否是Work3格式
            is_work3_format = False
            with open(source_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                if lines and 'FX5U&RCPU模板_AI测试' in lines[0]:
                    is_work3_format = True
            
            # 处理Work3格式
            if is_work3_format:
                with open(output_path, 'w', newline='', encoding=encoding) as f:
                    # 写入第一行（文件名）- 需要引号
                    f.write('"FX5U&RCPU模板_AI测试"\n')
                    
                    # 写入第二行（表头）- 使用制表符分隔
                    header = '"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"'
                    f.write(header + '\n')
                return True
            
            # 普通CSV格式
            # 读取源文件的表头
            fieldnames = []
            with open(source_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
            
            if not fieldnames:
                return False
            
            # 创建空文件（只写入表头）
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            
            return True
        except Exception as e:
            print(f"创建空文件失败: {str(e)}")
            return False
    
    def export_to_json(self, variables: List[Dict], output_path: str) -> bool:
        """
        导出变量到JSON文件
        
        参数:
            variables (List[Dict]): 变量列表
            output_path (str): 输出文件路径
            
        返回:
            bool: 导出是否成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(variables, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"导出JSON失败: {str(e)}")
            return False
    
    def export_to_format(self, variables: List[Dict], output_path: str, format_type: str, encoding: str = 'utf-8', fieldnames: List[str] = None) -> bool:
        """
        根据指定格式导出变量
        
        参数:
            variables (List[Dict]): 变量列表
            output_path (str): 输出文件路径
            format_type (str): 导出格式（csv, json）
            encoding (str): 文件编码
            fieldnames (List[str]): 字段名称列表
            
        返回:
            bool: 导出是否成功
        """
        format_type = format_type.lower()
        
        if format_type == 'csv':
            return self.export_to_csv(variables, output_path, encoding, fieldnames)
        elif format_type == 'json':
            return self.export_to_json(variables, output_path)
        else:
            print(f"不支持的导出格式: {format_type}")
            return False
    
    def convert_file(self, source_path: str, target_path: str, output_path: str) -> bool:
        """
        将目标文件转换为与源文件相同格式和编码的文件
        
        参数:
            source_path (str): 源文件路径（格式参考）
            target_path (str): 目标文件路径（待转换）
            output_path (str): 输出文件路径
            
        返回:
            bool: 转换是否成功
        """
        try:
            # 检测源文件编码
            encoding_detector = EncodingDetector()
            source_encoding = encoding_detector.detect_encoding(source_path)
            
            # 读取源文件内容，判断是否是Work3格式
            is_work3_format = False
            with open(source_path, 'r', encoding=source_encoding) as f:
                lines = f.readlines()
                if lines and 'FX5U&RCPU模板_AI测试' in lines[0]:
                    is_work3_format = True
            
            # 处理Work3格式
            if is_work3_format:
                # 解析目标文件
                target_encoding = encoding_detector.detect_encoding(target_path)
                variables = []
                
                with open(target_path, 'r', encoding=target_encoding, newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        var = {
                            'name': row.get('name', '').strip() if row.get('name') is not None else '',
                            'type': row.get('type', '').strip() if row.get('type') is not None else '',
                            'address': row.get('address', '').strip() if row.get('address') is not None else '',
                            'description': row.get('description', '').strip() if row.get('description') is not None else '',
                            'scope': row.get('scope', '').strip() if row.get('scope') is not None else ''
                        }
                        if var['name']:
                            variables.append(var)
                
                # 导出为Work3格式
                return self.export_to_work3_format(variables, output_path, source_encoding)
            
            # 普通CSV格式
            # 读取源文件的表头
            source_fieldnames = []
            with open(source_path, 'r', encoding=source_encoding, newline='') as f:
                reader = csv.DictReader(f)
                source_fieldnames = reader.fieldnames
            
            if not source_fieldnames:
                return False
            
            # 检测目标文件编码
            target_encoding = encoding_detector.detect_encoding(target_path)
            
            # 读取目标文件的内容
            target_variables = []
            with open(target_path, 'r', encoding=target_encoding, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 创建一个新的字典，用于存储转换后的字段
                    converted_row = {}
                    
                    # 遍历源文件的字段，将目标文件的对应字段映射过来
                    for source_field in source_fieldnames:
                        # 直接映射相同名称的字段
                        if source_field in row:
                            converted_row[source_field] = row[source_field].strip() if row[source_field] is not None else ''
                        # 特殊字段映射
                        elif source_field == '序号':
                            converted_row[source_field] = row.get('序号', '').strip() if row.get('序号') is not None else ''
                        elif source_field == '类别':
                            converted_row[source_field] = row.get('类型', '').strip() if row.get('类型') is not None else ''
                        elif source_field == '名称':
                            converted_row[source_field] = row.get('变量名', '').strip() if row.get('变量名') is not None else ''
                        elif source_field == '数据类型':
                            converted_row[source_field] = row.get('数据类型', '').strip() if row.get('数据类型') is not None else ''
                        elif source_field == '隐含初始值':
                            converted_row[source_field] = row.get('默认值', '').strip() if row.get('默认值') is not None else ''
                        elif source_field == '初始值':
                            converted_row[source_field] = row.get('初始值', '').strip() if row.get('初始值') is not None else ''
                        elif source_field == '掉电保持':
                            converted_row[source_field] = row.get('变量组', '').strip() if row.get('变量组') is not None else ''
                        elif source_field == '注释':
                            converted_row[source_field] = row.get('注释', '').strip() if row.get('注释') is not None else ''
                        # 通用字段映射
                        elif source_field == 'name' and '变量名' in row:
                            converted_row[source_field] = row['变量名'].strip() if row['变量名'] is not None else ''
                        elif source_field == 'name' and '名称' in row:
                            converted_row[source_field] = row['名称'].strip() if row['名称'] is not None else ''
                        elif source_field == 'name' and 'Name' in row:
                            converted_row[source_field] = row['Name'].strip() if row['Name'] is not None else ''
                        elif source_field == 'name' and 'Variable' in row:
                            converted_row[source_field] = row['Variable'].strip() if row['Variable'] is not None else ''
                        elif source_field == 'type' and '数据类型' in row:
                            converted_row[source_field] = row['数据类型'].strip() if row['数据类型'] is not None else ''
                        elif source_field == 'type' and 'Type' in row:
                            converted_row[source_field] = row['Type'].strip() if row['Type'] is not None else ''
                        elif source_field == 'type' and 'DataType' in row:
                            converted_row[source_field] = row['DataType'].strip() if row['DataType'] is not None else ''
                        elif source_field == 'address' and '地址' in row:
                            converted_row[source_field] = row['地址'].strip() if row['地址'] is not None else ''
                        elif source_field == 'address' and 'Address' in row:
                            converted_row[source_field] = row['Address'].strip() if row['Address'] is not None else ''
                        elif source_field == 'description' and '注释' in row:
                            converted_row[source_field] = row['注释'].strip() if row['注释'] is not None else ''
                        elif source_field == 'description' and 'Comment' in row:
                            converted_row[source_field] = row['Comment'].strip() if row['Comment'] is not None else ''
                        elif source_field == 'scope' and '作用域' in row:
                            converted_row[source_field] = row['作用域'].strip() if row['作用域'] is not None else ''
                        elif source_field == 'scope' and '类别' in row:
                            converted_row[source_field] = row['类别'].strip() if row['类别'] is not None else ''
                        else:
                            converted_row[source_field] = ''
                    target_variables.append(converted_row)
            
            # 导出为与源文件相同格式和编码的文件
            return self.export_to_csv(target_variables, output_path, source_encoding, source_fieldnames)
        except Exception as e:
            print(f"转换文件失败: {str(e)}")
            return False