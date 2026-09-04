# -*- coding: utf-8 -*-
"""
变量导出器
"""
import csv
import json
from typing import List, Dict, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Exporter:
    """变量导出器，用于将解析后的变量导出到不同格式的文件"""

    def __init__(self):
        # 修复P2-#19: 初始化导出器配置（当前无需额外配置）
        logger.debug("初始化变量导出器")
    
    def export_to_csv(self, variables: List[Dict], output_path: str, encoding: str = 'utf-8', fieldnames: List[str] = None) -> bool:
        """导出变量到CSV文件"""
        try:
            is_work3_format = False
            if fieldnames and len(fieldnames) == 1 and 'FX5U&RCPU模板_AI测试' in fieldnames[0]:
                is_work3_format = True
            
            if is_work3_format:
                return self.export_to_work3_format(variables, output_path, encoding)
            
            if not fieldnames:
                fieldnames = ['name', 'type', 'address', 'description', 'scope']
            
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for var in variables:
                    row = {}
                    for field in fieldnames:
                        row[field] = var.get(field, '')
                    writer.writerow(row)
            
            logger.info(f"CSV导出成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出CSV失败: {e}")
            return False
    
    def export_to_work3_format(self, variables: List[Dict], output_path: str, encoding: str = 'utf-16') -> bool:
        """导出变量到Work3格式文件"""
        try:
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                f.write('"FX5U&RCPU模板_AI测试"\n')
                
                header = '"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"'
                f.write(header + '\n')
                
                for var in variables:
                    scope = var.get('scope', 'VAR_INPUT')
                    name = var.get('name', '')
                    data_type = var.get('type', 'BOOL')
                    address = var.get('address', '')
                    description = var.get('description', '')
                    
                    fields = [
                        f'"{scope}"',
                        f'"{name}"',
                        f'"{data_type}"',
                        '""',
                        '"FALSE"',
                        '""',
                        '""',
                        f'"{description}"',
                        '""', '""', '""', '""',
                        '""', '""',
                        f'"{description}"',
                        '""', '""', '""', '""',
                        '""', '""', '""', '""', '""', '""', '""', '""',
                    ]
                    
                    row = '\t'.join(fields)
                    f.write(row + '\n')
            
            logger.info(f"Work3格式导出成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出Work3格式失败: {e}")
            return False
    
    def export_to_json(self, variables: List[Dict], output_path: str) -> bool:
        """导出变量到JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(variables, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON导出成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出JSON失败: {e}")
            return False
    
    def export_to_format(self, variables: List[Dict], output_path: str, format_type: str, encoding: str = 'utf-8', fieldnames: List[str] = None) -> bool:
        """根据指定格式导出变量"""
        format_type = format_type.lower()
        
        if format_type == 'csv':
            return self.export_to_csv(variables, output_path, encoding, fieldnames)
        elif format_type == 'json':
            return self.export_to_json(variables, output_path)
        elif format_type == 'work3':
            return self.export_to_work3_format(variables, output_path, encoding)
        else:
            logger.error(f"不支持的导出格式: {format_type}")
            return False
    
    def create_empty_file(self, source_path: str, output_path: str) -> bool:
        """创建与源文件格式和编码相同的空文件"""
        try:
            from ..utils.encoding_detector import EncodingDetector
            
            encoding = EncodingDetector.detect_encoding(source_path)
            
            is_work3_format = False
            with open(source_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                if lines and 'FX5U&RCPU模板_AI测试' in lines[0]:
                    is_work3_format = True
            
            if is_work3_format:
                with open(output_path, 'w', newline='', encoding=encoding) as f:
                    f.write('"FX5U&RCPU模板_AI测试"\n')
                    header = '"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"'
                    f.write(header + '\n')
                logger.info(f"创建Work3空文件成功: {output_path}")
                return True
            
            fieldnames = []
            with open(source_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
            
            if not fieldnames:
                return False
            
            with open(output_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
            
            logger.info(f"创建空文件成功: {output_path}")
            return True
        except Exception as e:
            logger.error(f"创建空文件失败: {e}")
            return False
    
    def convert_file(self, source_path: str, target_path: str, output_path: str) -> bool:
        """将目标文件转换为与源文件相同格式和编码的文件"""
        try:
            from ..utils.encoding_detector import EncodingDetector
            from ..parsers.parser_factory import ParserFactory
            
            source_encoding = EncodingDetector.detect_encoding(source_path)
            
            is_work3_format = False
            with open(source_path, 'r', encoding=source_encoding) as f:
                lines = f.readlines()
                if lines and 'FX5U&RCPU模板_AI测试' in lines[0]:
                    is_work3_format = True
            
            parser = ParserFactory.create_parser('auto', target_path)
            if not parser:
                logger.error("无法解析目标文件")
                return False
            
            variables = parser.parse()
            
            if is_work3_format:
                return self.export_to_work3_format(variables, output_path, source_encoding)
            
            source_fieldnames = []
            with open(source_path, 'r', encoding=source_encoding, newline='') as f:
                reader = csv.DictReader(f)
                source_fieldnames = reader.fieldnames
            
            if not source_fieldnames:
                return False
            
            return self.export_to_csv(variables, output_path, source_encoding, source_fieldnames)
        except Exception as e:
            logger.error(f"转换文件失败: {e}")
            return False
