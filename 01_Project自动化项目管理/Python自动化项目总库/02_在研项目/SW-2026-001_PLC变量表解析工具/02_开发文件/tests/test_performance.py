#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试脚本

测试工具的性能，包括解析速度、内存占用等
"""

import time
import os
import tempfile
import csv
import psutil
import sys
from parser.work3_parser import Work3Parser
from parser.autoshop_parser import AutoshopParser
from parser.codesys_parser import CodesysParser


class PerformanceTester:
    """
    性能测试类
    """
    
    def __init__(self):
        """
        初始化性能测试器
        """
        self.results = []
    
    def measure_memory_usage(self):
        """
        测量当前内存使用量
        
        返回:
            float: 内存使用量（MB）
        """
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_parse_performance(self, num_variables, parser_type='work3'):
        """
        测试解析性能
        
        Args:
            num_variables (int): 变量数量
            parser_type (str): 解析器类型
            
        返回:
            dict: 性能测试结果
        """
        print(f"\n{'='*60}")
        print(f"测试解析性能: {parser_type.upper()}格式，{num_variables}个变量")
        print(f"{'='*60}")
        
        # 创建测试文件
        temp_file = self._create_test_file(num_variables, parser_type)
        
        try:
            # 记录初始内存
            initial_memory = self.measure_memory_usage()
            print(f"初始内存: {initial_memory:.2f} MB")
            
            # 执行解析
            start_time = time.time()
            
            if parser_type == 'work3':
                parser = Work3Parser(temp_file)
            elif parser_type == 'autoshop':
                parser = AutoshopParser(temp_file)
            elif parser_type == 'codesys':
                parser = CodesysParser(temp_file)
            else:
                raise ValueError(f"不支持的解析器类型: {parser_type}")
            
            variables = parser.parse()
            
            end_time = time.time()
            
            # 记录结束内存
            final_memory = self.measure_memory_usage()
            print(f"结束内存: {final_memory:.2f} MB")
            print(f"内存增长: {final_memory - initial_memory:.2f} MB")
            
            # 计算性能指标
            parse_time = end_time - start_time
            print(f"解析时间: {parse_time:.3f} 秒")
            print(f"解析变量数: {len(variables)}")
            
            result = {
                'parser_type': parser_type,
                'num_variables': num_variables,
                'parse_time': parse_time,
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'memory_growth': final_memory - initial_memory,
                'variables_parsed': len(variables)
            }
            
            # 验证性能要求
            if num_variables <= 1000:
                if parse_time <= 1.0:
                    print("✓ 解析1000行变量表的时间不超过1秒 - 通过")
                else:
                    print(f"✗ 解析1000行变量表的时间超过1秒 - 失败 ({parse_time:.3f}秒)")
            elif num_variables <= 10000:
                if parse_time <= 10.0:
                    print("✓ 解析10000行变量表的时间不超过10秒 - 通过")
                else:
                    print(f"✗ 解析10000行变量表的时间超过10秒 - 失败 ({parse_time:.3f}秒)")
            
            if final_memory <= 100:
                print("✓ 内存占用不超过100MB - 通过")
            else:
                print(f"✗ 内存占用超过100MB - 失败 ({final_memory:.2f}MB)")
            
            self.results.append(result)
            return result
            
        finally:
            os.unlink(temp_file)
    
    def _create_test_file(self, num_variables, parser_type):
        """
        创建测试文件
        
        Args:
            num_variables (int): 变量数量
            parser_type (str): 解析器类型
            
        返回:
            str: 测试文件路径
        """
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        
        if parser_type == 'work3':
            temp_file.write('"FX5U&RCPU模板_AI测试"\n')
            temp_file.write('"类"\t"标签名"\t"数据类型"\t"常数"\t"初始值"\t"分配(软元件/标签)"\t"地址"\t"注释"\t"注释2"\t"注释3"\t"注释4"\t"注释5"\t"Japanese/日本語"\t"English"\t"Chinese Simplified/简体中文"\t"Korean/한국어"\t"Chinese Traditional/繁體中文"\t"German/Deutsch"\t"Italian/Italiano"\t"Reserved1"\t"Reserved2"\t"Reserved3"\t"Reserved4"\t"备注"\t"系统标签的关联"\t"系统标签名"\t"属性"\n')
            for i in range(num_variables):
                temp_file.write(f'"VAR_INPUT"\t"test_var_{i}"\t"BOOL"\t""\t"FALSE"\t""\t""\t"测试变量{i}"\t""\t""\t""\t""\t""\t""\t"测试变量{i}"\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""\n')
        elif parser_type == 'autoshop':
            writer = csv.DictWriter(temp_file, fieldnames=['变量名', '数据类型', '地址', '注释', '作用域'])
            writer.writeheader()
            for i in range(num_variables):
                writer.writerow({
                    '变量名': f'test_var_{i}',
                    '数据类型': 'BOOL',
                    '地址': f'D{i}',
                    '注释': f'测试变量{i}',
                    '作用域': 'VAR_INPUT'
                })
        elif parser_type == 'codesys':
            writer = csv.DictWriter(temp_file, fieldnames=['Name', 'Type', 'Address', 'Comment', 'Scope'])
            writer.writeheader()
            for i in range(num_variables):
                writer.writerow({
                    'Name': f'test_var_{i}',
                    'Type': 'BOOL',
                    'Address': f'D{i}',
                    'Comment': f'测试变量{i}',
                    'Scope': 'VAR_INPUT'
                })
        
        temp_file.flush()
        return temp_file.name
    
    def run_all_tests(self):
        """
        运行所有性能测试
        """
        print("\n" + "="*60)
        print("PLC变量表解析工具 - 性能测试")
        print("="*60)
        
        test_sizes = [100, 1000, 10000]
        
        for size in test_sizes:
            for parser_type in ['work3', 'autoshop', 'codesys']:
                try:
                    self.test_parse_performance(size, parser_type)
                except Exception as e:
                    print(f"测试失败: {str(e)}")
        
        self._print_summary()
    
    def _print_summary(self):
        """
        打印测试摘要
        """
        print("\n" + "="*60)
        print("性能测试摘要")
        print("="*60)
        
        for result in self.results:
            print(f"\n{result['parser_type'].upper()} - {result['num_variables']}个变量:")
            print(f"  解析时间: {result['parse_time']:.3f} 秒")
            print(f"  内存增长: {result['memory_growth']:.2f} MB")
            print(f"  解析变量: {result['variables_parsed']}")


def main():
    """
    主函数
    """
    tester = PerformanceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
