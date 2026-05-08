#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work3解析器

用于解析Work3格式的PLC变量表
"""

import csv
from typing import List, Dict
from parser.base_parser import BaseParser
from utils.encoding_detector import EncodingDetector
from utils.error_handler import ErrorHandler, ErrorCode


class Work3Parser(BaseParser):
    """
    Work3解析器
    
    用于解析Work3格式的PLC变量表
    """
    
    def parse(self) -> List[Dict]:
        """
        解析Work3格式的变量表
        
        返回:
            List[Dict]: 解析后的变量列表
        """
        self.variables = []
        error_handler = ErrorHandler()
        
        try:
            encoding_detector = EncodingDetector()
            encoding = encoding_detector.detect_encoding(self.file_path)
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"检测文件编码: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))
        
        try:
            with open(self.file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"读取文件: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))
        
        try:
            if len(lines) > 2:
                for line in lines[2:]:
                    line = line.strip()
                    if not line:
                        continue
                    
                    fields = line.split('\t')
                    
                    if len(fields) >= 8:
                        scope = fields[0].strip('"')
                        name = fields[1].strip('"')
                        data_type = fields[2].strip('"')
                        address = fields[6].strip()
                        description = fields[7].strip('"')
                        
                        variable = {
                            'name': name,
                            'type': data_type,
                            'address': address,
                            'description': description,
                            'scope': scope
                        }
                        
                        if variable['name']:
                            self.variables.append(variable)
        except Exception as e:
            error_info = error_handler.handle_exception(e, f"解析变量数据: {self.file_path}")
            raise Exception(error_handler.format_error_message(error_info))
        
        return self.variables