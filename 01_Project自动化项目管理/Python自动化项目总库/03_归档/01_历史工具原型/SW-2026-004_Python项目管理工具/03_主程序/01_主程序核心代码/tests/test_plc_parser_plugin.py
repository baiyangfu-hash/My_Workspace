# -*- coding: utf-8 -*-
"""
PLC变量表解析插件单元测试
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_FONT_DPI'] = '96'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEncodingDetector(unittest.TestCase):
    """编码检测器测试"""
    
    def test_detect_utf8_encoding(self):
        """测试UTF-8编码检测"""
        from src.plugins.plc_variable_parser.utils.encoding_detector import EncodingDetector
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write("变量名,数据类型,地址,注释\n")
            f.write("TestVar,BOOL,M0,测试变量\n")
            temp_path = f.name
        
        try:
            encoding = EncodingDetector.detect_encoding(temp_path)
            self.assertIn(encoding.lower(), ['utf-8', 'utf8'])
        finally:
            os.unlink(temp_path)
    
    def test_detect_gbk_encoding(self):
        """测试GBK编码检测"""
        from src.plugins.plc_variable_parser.utils.encoding_detector import EncodingDetector
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='gbk', suffix='.csv', delete=False) as f:
            f.write("变量名,数据类型,地址,注释\n")
            f.write("测试变量,BOOL,M0,测试\n")
            temp_path = f.name
        
        try:
            encoding = EncodingDetector.detect_encoding(temp_path)
            self.assertIn(encoding.lower(), ['gbk', 'gb2312'])
        finally:
            os.unlink(temp_path)
    
    def test_read_file_with_detection(self):
        """测试自动检测编码读取文件"""
        from src.plugins.plc_variable_parser.utils.encoding_detector import EncodingDetector
        
        content = "变量名,数据类型\nTestVar,BOOL\n"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            read_content, encoding = EncodingDetector.read_file_with_detection(temp_path)
            self.assertIn("变量名", read_content)
            self.assertIn("TestVar", read_content)
        finally:
            os.unlink(temp_path)


class TestAutoshopParser(unittest.TestCase):
    """Autoshop解析器测试"""
    
    def test_parse_autoshop_format(self):
        """测试解析Autoshop格式"""
        from src.plugins.plc_variable_parser.parsers.autoshop_parser import AutoshopParser
        
        content = "变量名,数据类型,地址,注释,作用域\nTestVar1,BOOL,M0,测试变量1,VAR_GLOBAL\nTestVar2,INT,D100,测试变量2,VAR_GLOBAL\n"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = AutoshopParser(temp_path)
            variables = parser.parse()
            
            self.assertEqual(len(variables), 2)
            self.assertEqual(variables[0]['name'], 'TestVar1')
            self.assertEqual(variables[0]['type'], 'BOOL')
            self.assertEqual(variables[0]['address'], 'M0')
            self.assertEqual(variables[0]['description'], '测试变量1')
            self.assertEqual(variables[1]['name'], 'TestVar2')
        finally:
            os.unlink(temp_path)
    
    def test_parse_empty_file(self):
        """测试解析空文件"""
        from src.plugins.plc_variable_parser.parsers.autoshop_parser import AutoshopParser
        
        content = "变量名,数据类型,地址,注释\n"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = AutoshopParser(temp_path)
            variables = parser.parse()
            self.assertEqual(len(variables), 0)
        finally:
            os.unlink(temp_path)


class TestWork3Parser(unittest.TestCase):
    """Work3解析器测试"""
    
    def test_parse_work3_format(self):
        """测试解析Work3格式"""
        from src.plugins.plc_variable_parser.parsers.work3_parser import Work3Parser
        
        content = '"FX5U&RCPU模板_AI测试"\n'
        content += '"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\n'
        content += '"VAR_GLOBAL"\t"TestVar1"\t"BOOL"\t""\t"FALSE"\t""\t"M0"\t"测试变量1"\n'
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-16', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = Work3Parser(temp_path)
            variables = parser.parse()
            
            self.assertEqual(len(variables), 1)
            self.assertEqual(variables[0]['name'], 'TestVar1')
            self.assertEqual(variables[0]['type'], 'BOOL')
            self.assertEqual(variables[0]['description'], '测试变量1')
        finally:
            os.unlink(temp_path)


class TestCodesysParser(unittest.TestCase):
    """Codesys解析器测试"""
    
    def test_parse_codesys_format(self):
        """测试解析Codesys格式"""
        from src.plugins.plc_variable_parser.parsers.codesys_parser import CodesysParser
        
        content = "Name,Type,Address,Comment,Scope\nTestVar1,BOOL,%IX0.0,Test Variable 1,VAR_GLOBAL\nTestVar2,INT,%IW0,Test Variable 2,VAR_INPUT\n"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            parser = CodesysParser(temp_path)
            variables = parser.parse()
            
            self.assertEqual(len(variables), 2)
            self.assertEqual(variables[0]['name'], 'TestVar1')
            self.assertEqual(variables[0]['type'], 'BOOL')
            self.assertEqual(variables[0]['address'], '%IX0.0')
        finally:
            os.unlink(temp_path)


class TestParserFactory(unittest.TestCase):
    """解析器工厂测试"""
    
    def test_create_autoshop_parser(self):
        """测试创建Autoshop解析器"""
        from src.plugins.plc_variable_parser.parsers.parser_factory import ParserFactory
        from src.plugins.plc_variable_parser.parsers.autoshop_parser import AutoshopParser
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write("变量名,数据类型\n")
            temp_path = f.name
        
        try:
            parser = ParserFactory.create_parser('autoshop', temp_path)
            self.assertIsInstance(parser, AutoshopParser)
        finally:
            os.unlink(temp_path)
    
    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        from src.plugins.plc_variable_parser.parsers.parser_factory import ParserFactory
        
        formats = ParserFactory.get_supported_formats()
        self.assertIn('autoshop', formats)
        self.assertIn('work3', formats)
        self.assertIn('codesys', formats)


class TestExporter(unittest.TestCase):
    """导出器测试"""
    
    def test_export_to_csv(self):
        """测试导出CSV"""
        from src.plugins.plc_variable_parser.exporters.exporter import Exporter
        
        variables = [
            {'name': 'TestVar1', 'type': 'BOOL', 'address': 'M0', 'description': '测试1', 'scope': 'VAR_GLOBAL'},
            {'name': 'TestVar2', 'type': 'INT', 'address': 'D100', 'description': '测试2', 'scope': 'VAR_GLOBAL'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            exporter = Exporter()
            success = exporter.export_to_csv(variables, temp_path)
            self.assertTrue(success)
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('TestVar1', content)
                self.assertIn('TestVar2', content)
        finally:
            os.unlink(temp_path)
    
    def test_export_to_json(self):
        """测试导出JSON"""
        from src.plugins.plc_variable_parser.exporters.exporter import Exporter
        
        variables = [
            {'name': 'TestVar1', 'type': 'BOOL', 'address': 'M0', 'description': '测试1'}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            exporter = Exporter()
            success = exporter.export_to_json(variables, temp_path)
            self.assertTrue(success)
            
            import json
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['name'], 'TestVar1')
        finally:
            os.unlink(temp_path)


class TestPLCVariableParserPlugin(unittest.TestCase):
    """插件主类测试"""
    
    def test_plugin_initialization(self):
        """测试插件初始化"""
        from src.plugins.plc_variable_parser import PLCVariableParserPlugin
        
        plugin = PLCVariableParserPlugin()
        self.assertEqual(plugin.plugin_id, 'plc_variable_parser')
        self.assertEqual(plugin.name, 'PLC变量表解析器')
        
        result = plugin.initialize({})
        self.assertTrue(result)
    
    def test_get_actions(self):
        """测试获取操作列表"""
        from src.plugins.plc_variable_parser import PLCVariableParserPlugin
        
        plugin = PLCVariableParserPlugin()
        actions = plugin.get_actions()
        
        self.assertEqual(len(actions), 5)
        action_ids = [a['id'] for a in actions]
        self.assertIn('parse_file', action_ids)
        self.assertIn('export_csv', action_ids)
        self.assertIn('export_json', action_ids)
    
    def test_parse_file_action(self):
        """测试解析文件操作"""
        from src.plugins.plc_variable_parser import PLCVariableParserPlugin
        
        content = "变量名,数据类型,地址,注释\nTestVar,BOOL,M0,测试\n"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            plugin = PLCVariableParserPlugin()
            plugin.initialize({})
            
            result, error = plugin.execute_action('parse_file', {'file_path': temp_path})
            
            self.assertEqual(error, "")
            self.assertIsNotNone(result)
            self.assertEqual(len(result['variables']), 1)
            self.assertEqual(result['variables'][0]['name'], 'TestVar')
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
