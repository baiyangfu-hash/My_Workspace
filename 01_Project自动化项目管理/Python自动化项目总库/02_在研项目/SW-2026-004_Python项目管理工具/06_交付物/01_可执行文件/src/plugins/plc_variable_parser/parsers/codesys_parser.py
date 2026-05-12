# -*- coding: utf-8 -*-
"""
Codesys解析器
"""
import csv
from typing import List, Dict
from .base_parser import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CodesysParser(BaseParser):
    """Codesys解析器，用于解析Codesys格式的PLC变量表"""
    
    def __init__(self, file_path: str, encoding: str = None):
        super().__init__(file_path, encoding)
        self._format_name = "Codesys"
    
    def parse(self) -> List[Dict]:
        """解析Codesys格式的变量表"""
        self.variables = []
        
        encoding = self._detect_encoding()
        logger.info(f"Codesys解析器使用编码: {encoding}")
        
        try:
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    variable = {
                        'name': row.get('Name', '').strip(),
                        'type': row.get('Type', '').strip(),
                        'address': row.get('Address', '').strip(),
                        'description': row.get('Comment', '').strip(),
                        'scope': row.get('Scope', '').strip(),
                        'default_value': row.get('Initial Value', '').strip(),
                        'group': '',
                    }
                    
                    if variable['name']:
                        self.variables.append(variable)
            
            logger.info(f"Codesys解析完成，共解析 {len(self.variables)} 个变量")
            return self.variables
            
        except Exception as e:
            logger.error(f"Codesys解析失败: {e}")
            raise
