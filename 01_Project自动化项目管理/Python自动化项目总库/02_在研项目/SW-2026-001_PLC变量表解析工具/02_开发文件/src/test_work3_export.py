#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Work3导出功能

验证修复后的导出器是否能够正确导出Work3格式的文件
"""

from parser.work3_parser import Work3Parser
from exporter.exporter import Exporter

# 源文件路径
source_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3.csv'

# 测试输出路径
test_output_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3-test.csv'

# 1. 解析源文件
print("=== 解析源文件 ===")
parser = Work3Parser(source_path)
try:
    variables = parser.parse()
    print(f"解析成功，共{len(variables)}个变量")
except Exception as e:
    print(f"解析失败: {str(e)}")
    exit(1)

# 2. 导出为Work3格式
print("\n=== 导出为Work3格式 ===")
exporter = Exporter()

# 读取源文件的字段名和编码
import chardet
encoding = None
fieldnames = None

with open(source_path, 'rb') as f:
    content = f.read()
    result = chardet.detect(content)
    encoding = result['encoding']

with open(source_path, 'r', encoding=encoding) as f:
    lines = f.readlines()
    if lines:
        fieldnames = [lines[0].strip()]

try:
    success = exporter.export_to_csv(variables, test_output_path, encoding, fieldnames)
    if success:
        print(f"导出成功: {test_output_path}")
    else:
        print("导出失败")
except Exception as e:
    print(f"导出失败: {str(e)}")
    exit(1)

# 3. 检查导出文件
print("\n=== 检查导出文件 ===")
import os
if os.path.exists(test_output_path):
    print(f"文件已创建，大小: {os.path.getsize(test_output_path)} 字节")
    
    # 读取导出文件的前几行
    with open(test_output_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
        print(f"行数: {len(lines)}")
        print("前5行内容:")
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            print(f"{i+1}: {line[:100]}..." if len(line) > 100 else f"{i+1}: {line}")
else:
    print("文件未创建")

print("\n测试完成！")