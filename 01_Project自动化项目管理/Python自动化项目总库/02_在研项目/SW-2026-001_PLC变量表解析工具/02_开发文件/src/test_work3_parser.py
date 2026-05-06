#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Work3解析器

验证修复后的Work3解析器是否能够正确解析Work3格式的PLC变量表
"""

from parser.work3_parser import Work3Parser

# Work3变量表文件路径
file_path = r'd:\BaiduSyncdisk\Trae_AI编程测试\汇川_Autoshop\自动化项目管理总库\01_公共资源库\01_Work3专属资源\模板库\FB\FB_导出PLC变量_输送线控制_work3.csv'

# 创建Work3解析器
parser = Work3Parser(file_path)

# 解析变量表
try:
    variables = parser.parse()
    print(f"解析成功，共{len(variables)}个变量")
    print("\n前5个变量:")
    for i, var in enumerate(variables[:5]):
        print(f"{i+1}. 名称: {var['name']}, 类型: {var['type']}, 作用域: {var['scope']}, 注释: {var['description']}")
except Exception as e:
    print(f"解析失败: {str(e)}")