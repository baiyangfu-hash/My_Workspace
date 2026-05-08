#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autoshop解析器

用于解析Autoshop格式的PLC变量表
"""

import csv
from typing import List, Dict
from parser.base_parser import BaseParser
from utils.encoding_detector import EncodingDetector
from utils.error_handler import ErrorHandler


class AutoshopParser(BaseParser):
    """
    Autoshop解析器
    
    用于解析Autoshop格式的PLC变量表
    """
    
    def parse(self) -> List[Dict]:
        """
        解析Autoshop格式的变量表
        
        返回:
            List[Dict]: 解析后的变量列表
        """
        self.variables = []
        error_handler = ErrorHandler()
        
        encoding = 'utf-8'
        try:
            encoding_detector = EncodingDetector()
            encoding = encoding_detector.detect_encoding(self.file_path)
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"检测文件编码: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))
        
        try:
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    variable = {
                        'name': row.get('变量名', '').strip() or row.get('名称', '').strip(),
                        'type': row.get('数据类型', '').strip(),
                        'address': row.get('地址', '').strip(),
                        'description': row.get('注释', '').strip(),
                        'scope': row.get('作用域', '').strip() or row.get('类别', '').strip()
                    }
                    
                    if variable['name']:
                        self.variables.append(variable)
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"解析文件: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))
        
        return self.variables
