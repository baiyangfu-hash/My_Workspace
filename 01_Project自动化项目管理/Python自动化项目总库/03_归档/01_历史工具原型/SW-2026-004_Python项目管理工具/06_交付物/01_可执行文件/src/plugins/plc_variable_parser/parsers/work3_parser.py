# -*- coding: utf-8 -*-
"""
Work3解析器
"""
from typing import List, Dict
from .base_parser import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Work3Parser(BaseParser):
    """Work3解析器，用于解析Work3格式的PLC变量表"""
    
    def __init__(self, file_path: str, encoding: str = None):
        super().__init__(file_path, encoding)
        self._format_name = "Work3"
    
    def parse(self) -> List[Dict]:
        """解析Work3格式的变量表"""
        self.variables = []
        
        encoding = self._detect_encoding()
        logger.info(f"Work3解析器使用编码: {encoding}")
        
        try:
            with open(self.file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Work3读取文件失败: {e}")
            raise
        
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
                            'scope': scope,
                            'default_value': '',
                            'group': '',
                        }
                        
                        if variable['name']:
                            self.variables.append(variable)
            
            logger.info(f"Work3解析完成，共解析 {len(self.variables)} 个变量")
            return self.variables
            
        except Exception as e:
            logger.error(f"Work3解析失败: {e}")
            raise
