# -*- coding: utf-8 -*-
"""
PLC变量表解析插件

解析和管理PLC变量表，支持Autoshop/Work3/Codesys格式
"""
from PyQt5.QtWidgets import QWidget
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PLCVariableParserPlugin:
    """PLC变量表解析插件"""
    
    plugin_id = "plc_variable_parser"
    
    def __init__(self):
        self.name = "PLC变量表解析器"
        self.version = "1.0.0"
        self.author = "Trae AI"
        self.description = "解析和管理PLC变量表，支持Autoshop/Work3/Codesys格式"
        self.config = {}
        self._widget = None
    
    def initialize(self, config: dict) -> bool:
        """初始化插件"""
        try:
            self.config = config or {}
            logger.info(f"PLC变量表解析插件初始化完成")
            return True
        except Exception as e:
            logger.error(f"插件初始化失败: {e}")
            return False
    
    def cleanup(self):
        """清理插件资源"""
        if self._widget:
            self._widget = None
        logger.info("PLC变量表解析插件资源已清理")
    
    def get_actions(self) -> list:
        """获取支持的操作"""
        return [
            {
                "id": "parse_file",
                "name": "解析变量表",
                "description": "解析PLC变量表文件"
            },
            {
                "id": "export_csv",
                "name": "导出CSV",
                "description": "导出变量表为CSV格式"
            },
            {
                "id": "export_json",
                "name": "导出JSON",
                "description": "导出变量表为JSON格式"
            },
            {
                "id": "convert_format",
                "name": "格式转换",
                "description": "转换变量表格式"
            },
            {
                "id": "create_empty",
                "name": "创建空文件",
                "description": "创建标准格式的空变量表"
            }
        ]
    
    def execute_action(self, action: str, params: dict) -> tuple:
        """执行操作"""
        from .parsers.parser_factory import ParserFactory
        from .exporters.exporter import Exporter
        
        try:
            if action == "parse_file":
                return self._parse_file(params, ParserFactory)
            elif action == "export_csv":
                return self._export_csv(params, Exporter)
            elif action == "export_json":
                return self._export_json(params, Exporter)
            elif action == "convert_format":
                return self._convert_format(params, ParserFactory, Exporter)
            elif action == "create_empty":
                return self._create_empty(params, Exporter)
            else:
                return None, f"不支持的操作: {action}"
        except Exception as e:
            logger.error(f"执行操作失败: {action}, 错误: {e}")
            return None, str(e)
    
    def get_widget(self, parent=None) -> QWidget:
        """获取插件UI组件"""
        if not self._widget:
            from .ui.parser_widget import ParserWidget
            self._widget = ParserWidget(parent, self.config)
        return self._widget
    
    def _parse_file(self, params: dict, parser_factory) -> tuple:
        """解析文件"""
        file_path = params.get("file_path")
        format_type = params.get("format_type", "auto")
        encoding = params.get("encoding", "auto")
        
        if not file_path:
            return None, "缺少文件路径参数"
        
        parser = parser_factory.create_parser(format_type, file_path, encoding)
        if not parser:
            return None, f"不支持的格式: {format_type}"
        
        variables = parser.parse()
        return {
            "variables": variables,
            "format": parser.get_format_name(),
            "encoding": parser.get_encoding()
        }, ""
    
    def _export_csv(self, params: dict, exporter) -> tuple:
        """导出CSV"""
        variables = params.get("variables", [])
        output_path = params.get("output_path")
        encoding = params.get("encoding", "utf-8")
        fieldnames = params.get("fieldnames")
        
        if not output_path:
            return None, "缺少输出路径参数"
        
        success = exporter.export_to_csv(variables, output_path, encoding, fieldnames)
        if success:
            return {"output_path": output_path}, ""
        return None, "导出CSV失败"
    
    def _export_json(self, params: dict, exporter) -> tuple:
        """导出JSON"""
        variables = params.get("variables", [])
        output_path = params.get("output_path")
        
        if not output_path:
            return None, "缺少输出路径参数"
        
        success = exporter.export_to_json(variables, output_path)
        if success:
            return {"output_path": output_path}, ""
        return None, "导出JSON失败"
    
    def _convert_format(self, params: dict, parser_factory, exporter) -> tuple:
        """格式转换"""
        source_path = params.get("source_path")
        target_format = params.get("target_format")
        output_path = params.get("output_path")
        
        if not all([source_path, target_format, output_path]):
            return None, "缺少必要参数"
        
        parser = parser_factory.create_parser("auto", source_path)
        if not parser:
            return None, "无法识别源文件格式"
        
        variables = parser.parse()
        success = exporter.export_to_format(variables, output_path, target_format)
        
        if success:
            return {"output_path": output_path}, ""
        return None, "格式转换失败"
    
    def _create_empty(self, params: dict, exporter) -> tuple:
        """创建空文件"""
        source_path = params.get("source_path")
        output_path = params.get("output_path")
        
        if not all([source_path, output_path]):
            return None, "缺少必要参数"
        
        success = exporter.create_empty_file(source_path, output_path)
        if success:
            return {"output_path": output_path}, ""
        return None, "创建空文件失败"
