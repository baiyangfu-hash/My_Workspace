#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试解析器

验证解析器功能的正确性和可靠性
"""

import pytest
import os
import tempfile
import csv
from parser.work3_parser import Work3Parser
from parser.autoshop_parser import AutoshopParser
from parser.codesys_parser import CodesysParser


class TestWork3Parser:
    """
    Work3解析器测试类
    """
    
    def test_parse_work3_format(self):
        """
        测试Work3格式解析
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-16', delete=False, newline='') as f:
            f.write('"FX5U&RCPU模板_AI测试"\n')
            f.write('"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"\n')
            f.write('"VAR_INPUT"\t"i_Sensor1"\t"BOOL"\t""\t"FALSE"\t""\t""\t"一号位置传感器"\t""\t""\t""\t""\t""\t""\t"一号位置传感器"\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\n')
            f.flush()
            temp_path = f.name
        
        try:
            parser = Work3Parser(temp_path)
            variables = parser.parse()
            assert len(variables) == 1, f"应解析出1个变量，实际为: {len(variables)}"
            assert variables[0]['name'] == 'i_Sensor1', f"变量名应为i_Sensor1，实际为: {variables[0]['name']}"
            assert variables[0]['type'] == 'BOOL', f"变量类型应为BOOL，实际为: {variables[0]['type']}"
            assert variables[0]['scope'] == 'VAR_INPUT', f"变量作用域应为VAR_INPUT，实际为: {variables[0]['scope']}"
        finally:
            os.unlink(temp_path)
    
    def test_parse_empty_file(self):
        """
        测试解析空文件
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-16', delete=False, newline='') as f:
            f.write('"FX5U&RCPU模板_AI测试"\n')
            f.write('"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"\n')
            f.flush()
            temp_path = f.name
        
        try:
            parser = Work3Parser(temp_path)
            variables = parser.parse()
            assert len(variables) == 0, f"空文件应解析出0个变量，实际为: {len(variables)}"
        finally:
            os.unlink(temp_path)


class TestAutoshopParser:
    """
    Autoshop解析器测试类
    """
    
    def test_parse_autoshop_format(self):
        """
        测试Autoshop格式解析
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['变量名', '数据类型', '地址', '注释', '作用域'])
            writer.writeheader()
            writer.writerow({
                '变量名': 'test_var',
                '数据类型': 'BOOL',
                '地址': 'D0',
                '注释': '测试变量',
                '作用域': 'VAR_INPUT'
            })
            f.flush()
            temp_path = f.name
        
        try:
            parser = AutoshopParser(temp_path)
            variables = parser.parse()
            assert len(variables) == 1, f"应解析出1个变量，实际为: {len(variables)}"
            assert variables[0]['name'] == 'test_var', f"变量名应为test_var，实际为: {variables[0]['name']}"
            assert variables[0]['type'] == 'BOOL', f"变量类型应为BOOL，实际为: {variables[0]['type']}"
        finally:
            os.unlink(temp_path)
    
    def test_parse_empty_file(self):
        """
        测试解析空文件
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['变量名', '数据类型', '地址', '注释', '作用域'])
            writer.writeheader()
            f.flush()
            temp_path = f.name
        
        try:
            parser = AutoshopParser(temp_path)
            variables = parser.parse()
            assert len(variables) == 0, f"空文件应解析出0个变量，实际为: {len(variables)}"
        finally:
            os.unlink(temp_path)


class TestCodesysParser:
    """
    Codesys解析器测试类
    """
    
    def test_parse_codesys_format(self):
        """
        测试Codesys格式解析
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'Type', 'Address', 'Comment', 'Scope'])
            writer.writeheader()
            writer.writerow({
                'Name': 'test_var',
                'Type': 'BOOL',
                'Address': 'D0',
                'Comment': '测试变量',
                'Scope': 'VAR_INPUT'
            })
            f.flush()
            temp_path = f.name
        
        try:
            parser = CodesysParser(temp_path)
            variables = parser.parse()
            assert len(variables) == 1, f"应解析出1个变量，实际为: {len(variables)}"
            assert variables[0]['name'] == 'test_var', f"变量名应为test_var，实际为: {variables[0]['name']}"
            assert variables[0]['type'] == 'BOOL', f"变量类型应为BOOL，实际为: {variables[0]['type']}"
        finally:
            os.unlink(temp_path)
    
    def test_parse_empty_file(self):
        """
        测试解析空文件
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', encoding='utf-8', delete=False, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'Type', 'Address', 'Comment', 'Scope'])
            writer.writeheader()
            f.flush()
            temp_path = f.name
        
        try:
            parser = CodesysParser(temp_path)
            variables = parser.parse()
            assert len(variables) == 0, f"空文件应解析出0个变量，实际为: {len(variables)}"
        finally:
            os.unlink(temp_path)
