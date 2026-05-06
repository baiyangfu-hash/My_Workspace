#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换器工厂

用于创建不同格式的转换器实例
"""

from typing import Optional
from .base_converter import BaseConverter


class ConverterFactory:
    """
    转换器工厂类
    
    用于创建不同格式的转换器实例
    """
    
    @staticmethod
    def create_converter(source_format: str, target_format: str) -> Optional[BaseConverter]:
        """
        创建转换器实例
        
        参数:
            source_format (str): 源格式
            target_format (str): 目标格式
            
        返回:
            Optional[BaseConverter]: 转换器实例，如果不支持则返回None
        """
        # 目前实现一个通用转换器，后续可以扩展为针对特定格式的转换器
        class GenericConverter(BaseConverter):
            """
            通用转换器
            
            用于基本的格式转换
            """
            
            def convert(self, variables: list) -> list:
                """
                转换变量格式
                
                参数:
                    variables (list): 原始变量列表
                    
                返回:
                    list: 转换后的变量列表
                """
                # 基本转换：保持变量结构不变
                # 后续可以根据需要添加特定格式的转换逻辑
                return variables
        
        # 对于所有格式组合，返回通用转换器
        # 后续可以根据需要添加特定格式的转换器
        return GenericConverter()
    
    @staticmethod
    def get_supported_formats() -> list:
        """
        获取支持的格式列表
        
        返回:
            list: 支持的格式列表
        """
        return ['autoshop', 'work3', 'codesys', 'csv', 'json']
