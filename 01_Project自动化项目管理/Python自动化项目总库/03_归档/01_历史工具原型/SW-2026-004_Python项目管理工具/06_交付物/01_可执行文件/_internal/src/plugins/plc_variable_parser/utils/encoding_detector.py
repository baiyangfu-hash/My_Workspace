# -*- coding: utf-8 -*-
"""
编码检测工具类
"""
import chardet
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EncodingDetector:
    """编码检测工具类，用于检测文件编码"""
    
    @staticmethod
    def detect_encoding(file_path, manual_encoding=None):
        """
        检测文件编码
        
        Args:
            file_path (str): 文件路径
            manual_encoding (str): 手动指定的编码，如果提供则优先使用
            
        Returns:
            str: 检测到的编码
        """
        if manual_encoding and manual_encoding != 'auto':
            return EncodingDetector._validate_encoding(manual_encoding)
        
        with open(file_path, 'rb') as f:
            content = f.read()
            
            common_encodings = ['gbk', 'gb2312', 'utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be']
            
            for encoding in common_encodings:
                try:
                    decoded = content.decode(encoding)
                    if '\ufffd' not in decoded:
                        result = chardet.detect(content)
                        if result['confidence'] > 0.7 or result['encoding'].lower().replace('-', '') == encoding.lower().replace('-', ''):
                            return encoding
                except (UnicodeDecodeError, LookupError):
                    continue
            
            result = chardet.detect(content)
            encoding = result['encoding']
            
            if result['confidence'] < 0.7:
                for encoding in common_encodings:
                    try:
                        content.decode(encoding)
                        return encoding
                    except (UnicodeDecodeError, LookupError):
                        continue
            
            return EncodingDetector._normalize_encoding(encoding)
    
    @staticmethod
    def _validate_encoding(encoding):
        """验证编码是否有效"""
        try:
            'test'.encode(encoding)
            return EncodingDetector._normalize_encoding(encoding)
        except LookupError:
            raise ValueError(f"不支持的编码: {encoding}")
    
    @staticmethod
    def _normalize_encoding(encoding):
        """标准化编码名称"""
        if not encoding:
            return 'utf-8'
        
        encoding = encoding.lower().replace('_', '-')
        
        encoding_map = {
            'utf8': 'utf-8',
            'utf8sig': 'utf-8-sig',
            'utf16': 'utf-16',
            'utf16le': 'utf-16-le',
            'utf16be': 'utf-16-be',
            'gb18030': 'gbk',
            'gb2312': 'gb2312',
            'chinese': 'gbk',
        }
        
        return encoding_map.get(encoding, encoding)
    
    @staticmethod
    def read_file_with_detection(file_path, manual_encoding=None):
        """自动检测编码并读取文件"""
        encoding = EncodingDetector.detect_encoding(file_path, manual_encoding)
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except UnicodeDecodeError as e:
            fallback_encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for fallback_encoding in fallback_encodings:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        return f.read(), fallback_encoding
                except UnicodeDecodeError:
                    continue
            raise Exception(f"无法解码文件 {file_path}，尝试的编码: {encoding}，错误: {str(e)}")
    
    @staticmethod
    def get_supported_encodings():
        """获取支持的编码列表"""
        return [
            ('自动检测', None),
            ('UTF-8', 'utf-8'),
            ('UTF-8 with BOM', 'utf-8-sig'),
            ('GBK (简体中文)', 'gbk'),
            ('GB2312 (简体中文)', 'gb2312'),
            ('UTF-16', 'utf-16'),
            ('UTF-16 LE', 'utf-16-le'),
            ('UTF-16 BE', 'utf-16-be'),
            ('Latin-1', 'latin-1'),
        ]
