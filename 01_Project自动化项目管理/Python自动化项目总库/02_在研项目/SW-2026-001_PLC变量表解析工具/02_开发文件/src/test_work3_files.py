#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Work3文件格式

检查两个Work3文件的格式差异
"""

import chardet

# 源文件路径
source_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3.csv'

# 修改后的文件路径
modified_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3-侧四.csv'

# 检测文件编码并读取内容
def check_file(file_path, name):
    print(f"\n=== 检查 {name} ===")
    
    # 检测编码
    with open(file_path, 'rb') as f:
        content = f.read()
        result = chardet.detect(content)
        encoding = result['encoding']
        confidence = result['confidence']
        print(f"编码: {encoding} (置信度: {confidence:.2f})")
    
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            print(f"行数: {len(lines)}")
            
            # 打印前5行
            print("前5行内容:")
            for i, line in enumerate(lines[:5]):
                line = line.strip()
                print(f"{i+1}: {line[:100]}..." if len(line) > 100 else f"{i+1}: {line}")
                
                # 分割字段并打印字段数
                if '\t' in line:
                    fields = line.split('\t')
                    print(f"  字段数: {len(fields)}")
                    print(f"  前3个字段: {fields[:3]}")
    except Exception as e:
        print(f"读取失败: {str(e)}")

# 检查源文件
check_file(source_path, "源文件")

# 检查修改后的文件
check_file(modified_path, "修改后的文件")