#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析器工厂

用于根据不同的PLC软件格式创建对应的解析器实例
"""

from typing import Optional
from .base_parser import BaseParser
from .autoshop_parser import AutoshopParser
from .work3_parser import Work3Parser
from .codesys_parser import CodesysParser
from .scl_parser import SclParser


class ParserFactory:
    """
    解析器工厂类
    
    用于根据不同的PLC软件格式创建对应的解析器实例
    """
    
    @staticmethod
    def create_parser(plc_format: str, file_path: str) -> Optional[BaseParser]:
        """
        创建解析器实例
        
        参数:
            plc_format (str): PLC软件格式（autoshop, work3, codesys, scl）
            file_path (str): 变量表文件路径
            
        返回:
            Optional[BaseParser]: 解析器实例，如果格式不支持则返回None
        """
        plc_format = plc_format.lower()
        
        if plc_format == 'autoshop':
            return AutoshopParser(file_path)
        elif plc_format == 'work3':
            return Work3Parser(file_path)
        elif plc_format == 'codesys':
            return CodesysParser(file_path)
        elif plc_format == 'scl':
            return SclParser(file_path)
        else:
            return None
    
    @staticmethod
    def get_supported_formats() -> list:
        """
        获取支持的PLC格式列表
        
        返回:
            list: 支持的格式列表
        """
        return ['autoshop', 'work3', 'codesys', 'scl']
