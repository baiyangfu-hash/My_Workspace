# -*- coding: utf-8 -*-
"""
解析器工厂
"""
from typing import Optional, List
from .base_parser import BaseParser
from .autoshop_parser import AutoshopParser
from .work3_parser import Work3Parser
from .codesys_parser import CodesysParser
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ParserFactory:
    """解析器工厂类，用于根据不同的PLC软件格式创建对应的解析器实例"""
    
    _parsers = {
        'autoshop': AutoshopParser,
        'work3': Work3Parser,
        'codesys': CodesysParser,
    }
    
    @classmethod
    def create_parser(cls, plc_format: str, file_path: str, encoding: str = None) -> Optional[BaseParser]:
        """
        创建解析器实例
        
        Args:
            plc_format (str): PLC软件格式（autoshop, work3, codesys, auto）
            file_path (str): 变量表文件路径
            encoding (str): 指定编码
            
        Returns:
            Optional[BaseParser]: 解析器实例，如果格式不支持则返回None
        """
        plc_format = plc_format.lower() if plc_format else 'auto'
        
        if plc_format == 'auto':
            return cls._auto_detect_format(file_path, encoding)
        
        parser_class = cls._parsers.get(plc_format)
        if parser_class:
            logger.info(f"创建解析器: {plc_format}")
            return parser_class(file_path, encoding)
        
        logger.warning(f"不支持的PLC格式: {plc_format}")
        return None
    
    @classmethod
    def _auto_detect_format(cls, file_path: str, encoding: str = None) -> Optional[BaseParser]:
        """自动检测文件格式"""
        from ..utils.encoding_detector import EncodingDetector
        
        detected_encoding = encoding or EncodingDetector.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=detected_encoding) as f:
                first_line = f.readline().strip()
                second_line = f.readline().strip()
                
                if 'FX5U&RCPU模板_AI测试' in first_line or '类' in second_line:
                    logger.info("自动检测格式: Work3")
                    return Work3Parser(file_path, encoding)
                
                f.seek(0)
                reader_cls = __import__('csv').DictReader(f)
                fieldnames = reader_cls.fieldnames
                
                if fieldnames:
                    fieldnames_lower = [f.lower() for f in fieldnames]
                    
                    if any(f in fieldnames_lower for f in ['name', 'type', 'address', 'comment']):
                        logger.info("自动检测格式: Codesys")
                        return CodesysParser(file_path, encoding)
                    
                    if any(f in fieldnames_lower for f in ['变量名', '名称', '数据类型', '注释']):
                        logger.info("自动检测格式: Autoshop")
                        return AutoshopParser(file_path, encoding)
        except Exception as e:
            logger.warning(f"自动检测格式失败: {e}")
        
        logger.info("自动检测格式失败，使用默认: Autoshop")
        return AutoshopParser(file_path, encoding)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """获取支持的PLC格式列表"""
        return list(cls._parsers.keys())
    
    @classmethod
    def get_format_display_names(cls) -> dict:
        """获取格式显示名称"""
        return {
            'autoshop': 'Autoshop (汇川)',
            'work3': 'Work3 (三菱)',
            'codesys': 'Codesys (国际标准)',
            'auto': '自动检测'
        }
