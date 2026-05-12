# -*- coding: utf-8 -*-
"""
基础解析器类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseParser(ABC):
    """基础解析器类，所有PLC变量表解析器的基类"""
    
    def __init__(self, file_path: str, encoding: str = None):
        """
        初始化解析器
        
        Args:
            file_path (str): 变量表文件路径
            encoding (str): 指定编码，None为自动检测
        """
        self.file_path = file_path
        self.encoding = encoding
        self.variables: List[Dict] = []
        self._detected_encoding: Optional[str] = None
        self._format_name: str = "Unknown"
    
    @abstractmethod
    def parse(self) -> List[Dict]:
        """
        解析变量表
        
        Returns:
            List[Dict]: 解析后的变量列表
        """
        pass
    
    def get_variables(self) -> List[Dict]:
        """获取解析后的变量列表"""
        return self.variables
    
    def get_encoding(self) -> Optional[str]:
        """获取检测到的编码"""
        return self._detected_encoding
    
    def get_format_name(self) -> str:
        """获取格式名称"""
        return self._format_name
    
    def _detect_encoding(self) -> str:
        """检测文件编码"""
        from ..utils.encoding_detector import EncodingDetector
        
        if self.encoding and self.encoding != 'auto':
            return self.encoding
        
        detected = EncodingDetector.detect_encoding(self.file_path)
        self._detected_encoding = detected
        return detected
