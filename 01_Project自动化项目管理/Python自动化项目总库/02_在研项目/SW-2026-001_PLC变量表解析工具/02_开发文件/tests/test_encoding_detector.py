#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编码检测器

验证编码检测功能的正确性和可靠性
"""

import pytest
import os
import tempfile
from utils.encoding_detector import EncodingDetector


class TestEncodingDetector:
    """
    编码检测器测试类
    """
    
    def test_detect_utf8_encoding(self):
        """
        测试UTF-8编码检测
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write('测试内容')
            f.flush()
            temp_path = f.name
        
        try:
            detected_encoding = EncodingDetector.detect_encoding(temp_path)
            assert detected_encoding in ['utf-8', 'utf-8-sig'], f"检测到的编码应为UTF-8，实际为: {detected_encoding}"
        finally:
            os.unlink(temp_path)
    
    def test_detect_gbk_encoding(self):
        """
        测试GBK编码检测
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='gbk', delete=False) as f:
            f.write('测试内容')
            f.flush()
            temp_path = f.name
        
        try:
            detected_encoding = EncodingDetector.detect_encoding(temp_path)
            assert 'gbk' in detected_encoding.lower(), f"检测到的编码应为GBK，实际为: {detected_encoding}"
        finally:
            os.unlink(temp_path)
    
    def test_manual_encoding_override(self):
        """
        测试手动指定编码覆盖自动检测
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write('测试内容')
            f.flush()
            temp_path = f.name
        
        try:
            detected_encoding = EncodingDetector.detect_encoding(temp_path, manual_encoding='gbk')
            assert detected_encoding == 'gbk', f"手动指定的编码应优先，实际为: {detected_encoding}"
        finally:
            os.unlink(temp_path)
    
    def test_read_file_with_detection(self):
        """
        测试自动检测编码并读取文件
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', encoding='utf-8', delete=False) as f:
            f.write('测试内容')
            f.flush()
            temp_path = f.name
        
        try:
            content, encoding = EncodingDetector.read_file_with_detection(temp_path)
            assert content == '测试内容', "读取的内容应与写入的内容一致"
            assert encoding in ['utf-8', 'utf-8-sig'], f"检测到的编码应为UTF-8，实际为: {encoding}"
        finally:
            os.unlink(temp_path)
    
    def test_normalize_encoding(self):
        """
        测试编码名称标准化
        """
        assert EncodingDetector._normalize_encoding('utf8') == 'utf-8'
        assert EncodingDetector._normalize_encoding('UTF8') == 'utf-8'
        assert EncodingDetector._normalize_encoding('utf16') == 'utf-16'
        assert EncodingDetector._normalize_encoding('gb18030') == 'gbk'
    
    def test_validate_encoding(self):
        """
        测试编码验证
        """
        assert EncodingDetector._validate_encoding('utf-8') == 'utf-8'
        assert EncodingDetector._validate_encoding('gbk') == 'gbk'
        
        with pytest.raises(ValueError):
            EncodingDetector._validate_encoding('invalid-encoding')
    
    def test_get_supported_encodings(self):
        """
        测试获取支持的编码列表
        """
        encodings = EncodingDetector.get_supported_encodings()
        assert len(encodings) > 0, "应返回支持的编码列表"
        assert encodings[0] == ('自动检测', None), "第一个选项应为自动检测"
