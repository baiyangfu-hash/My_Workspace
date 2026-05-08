#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础解析器类

定义所有解析器的通用接口和方法
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseParser(ABC):
    """
    基础解析器类
    
    所有PLC变量表解析器的基类，定义通用接口和方法
    """
    
    def __init__(self, file_path: str):
        """
        初始化解析器
        
        参数:
            file_path (str): 变量表文件路径
        """
        self.file_path = file_path
        self.variables: List[Dict] = []
    
    @abstractmethod
    def parse(self) -> List[Dict]:
        """
        解析变量表
        
        返回:
            List[Dict]: 解析后的变量列表
        """
        pass
    
    def get_variables(self) -> List[Dict]:
        """
        获取解析后的变量列表
        
        返回:
            List[Dict]: 变量列表
        """
        return self.variables
