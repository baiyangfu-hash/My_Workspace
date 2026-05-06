#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础转换器类

定义所有格式转换器的通用接口和方法
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseConverter(ABC):
    """
    基础转换器类
    
    所有PLC变量格式转换器的基类，定义通用接口和方法
    """
    
    def __init__(self):
        """
        初始化转换器
        """
        pass
    
    @abstractmethod
    def convert(self, variables: List[Dict]) -> List[Dict]:
        """
        转换变量格式
        
        参数:
            variables (List[Dict]): 原始变量列表
            
        返回:
            List[Dict]: 转换后的变量列表
        """
        pass
