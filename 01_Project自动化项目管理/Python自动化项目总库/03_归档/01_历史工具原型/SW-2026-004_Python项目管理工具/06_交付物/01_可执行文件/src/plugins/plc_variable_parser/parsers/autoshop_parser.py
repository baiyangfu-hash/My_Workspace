# -*- coding: utf-8 -*-
"""
Autoshop解析器
"""
import csv
from typing import List, Dict
from .base_parser import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class AutoshopParser(BaseParser):
    """Autoshop解析器，用于解析Autoshop格式的PLC变量表"""
    
    def __init__(self, file_path: str, encoding: str = None):
        super().__init__(file_path, encoding)
        self._format_name = "Autoshop"
    
    def parse(self) -> List[Dict]:
        """解析Autoshop格式的变量表"""
        self.variables = []
        
        encoding = self._detect_encoding()
        logger.info(f"Autoshop解析器使用编码: {encoding}")
        
        try:
            with open(self.file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    variable = {
                        'name': row.get('变量名', '').strip() or row.get('名称', '').strip(),
                        'type': row.get('数据类型', '').strip(),
                        'address': row.get('地址', '').strip(),
                        'description': row.get('注释', '').strip(),
                        'scope': row.get('作用域', '').strip() or row.get('类别', '').strip(),
                        'default_value': row.get('初始值', '').strip() or row.get('默认值', '').strip(),
                        'group': row.get('变量组', '').strip(),
                    }
                    
                    if variable['name']:
                        self.variables.append(variable)
            
            logger.info(f"Autoshop解析完成，共解析 {len(self.variables)} 个变量")
            return self.variables
            
        except Exception as e:
            logger.error(f"Autoshop解析失败: {e}")
            raise
