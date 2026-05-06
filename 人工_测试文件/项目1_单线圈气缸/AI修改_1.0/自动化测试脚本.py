#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试脚本
用于验证自动化工具的执行结果
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('自动化测试日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 定义项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 定义自动化工具路径
PYTHON_PATH = sys.executable
AI_TOOLS_PATH = "d:\\BaiduSyncdisk\\Trae_AI编程测试\\汇川_Autoshop\\AI_Python辅助工具"
BASE_CORE_TOOLS_PATH = os.path.join(AI_TOOLS_PATH, "基础核心工具")

# 定义测试文件路径
VARIABLE_TABLE_FILE = os.path.join(PROJECT_ROOT, "变量表格", "FB_导入变量_单线圈气缸控制_20260125_1657_v1.0.4.csv")
PROGRAM_FILE = os.path.join(PROJECT_ROOT, "程序文件", "FB_气缸控制_20260125_1657_v1.0.4.scl")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "配置文件", "version_sync_config.json")

class AutomationTest:
    """自动化测试类"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
    
    def run_command(self, command, timeout=30):
        """运行命令并返回结果"""
        logging.info(f"执行命令: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=timeout
            )
            
            # 尝试使用不同编码解码输出
            stdout = ""
            stderr = ""
            
            # 尝试GBK编码（Autoshop相关工具常用）
            try:
                stdout = result.stdout.decode('gbk')
                stderr = result.stderr.decode('gbk')
            except UnicodeDecodeError:
                # 尝试UTF-8编码
                try:
                    stdout = result.stdout.decode('utf-8')
                    stderr = result.stderr.decode('utf-8')
                except UnicodeDecodeError:
                    # 尝试Latin-1编码
                    stdout = result.stdout.decode('latin-1')
                    stderr = result.stderr.decode('latin-1')
        
            return {
                "returncode": result.returncode,
                "stdout": stdout,
                "stderr": stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "命令执行超时"
            }
    
    def test_check_encoding(self):
        """测试check_encoding.py工具"""
        logging.info("=== 测试check_encoding.py工具 ===")
        
        # 测试变量表文件编码
        command = [
            PYTHON_PATH,
            os.path.join(BASE_CORE_TOOLS_PATH, "check_encoding.py"),
            VARIABLE_TABLE_FILE
        ]
        
        result = self.run_command(command)
        
        # 检查结果
        test_passed = False
        if result["returncode"] == 0:
            if "文件编码为GBK" in result["stdout"]:
                test_passed = True
                logging.info("✓ 变量表文件编码检查通过，文件使用GBK编码")
            else:
                logging.error(f"✗ 变量表文件编码检查失败，预期GBK编码，但检测结果为: {result['stdout']}")
        else:
            logging.error(f"✗ 变量表文件编码检查失败，命令返回码: {result['returncode']}, 错误信息: {result['stderr']}")
        
        self.test_results.append({
            "test_name": "check_encoding",
            "test_target": "变量表文件编码检查",
            "status": "PASS" if test_passed else "FAIL",
            "details": result
        })
    
    def test_verify_csv_format(self):
        """测试verify_csv_format.py工具"""
        logging.info("=== 测试verify_csv_format.py工具 ===")
        
        # 测试变量表文件格式
        command = [
            PYTHON_PATH,
            os.path.join(BASE_CORE_TOOLS_PATH, "verify_csv_format.py"),
            VARIABLE_TABLE_FILE
        ]
        
        result = self.run_command(command)
        
        # 检查结果
        test_passed = False
        if result["returncode"] == 0:
            if "验证通过" in result["stdout"]:
                test_passed = True
                logging.info("✓ 变量表文件格式检查通过")
            else:
                logging.error(f"✗ 变量表文件格式检查失败: {result['stdout']}")
        else:
            logging.error(f"✗ 变量表文件格式检查失败，命令返回码: {result['returncode']}, 错误信息: {result['stderr']}")
        
        self.test_results.append({
            "test_name": "verify_csv_format",
            "test_target": "变量表文件格式检查",
            "status": "PASS" if test_passed else "FAIL",
            "details": result
        })
    
    def test_version_manager(self):
        """测试version_manager.py工具"""
        logging.info("=== 测试version_manager.py工具 ===")
        
        # 测试版本管理器检查功能
        command = [
            PYTHON_PATH,
            os.path.join(BASE_CORE_TOOLS_PATH, "version_manager.py"),
            "check",
            "--file",
            VARIABLE_TABLE_FILE
        ]
        
        result = self.run_command(command)
        
        # 检查结果
        test_passed = False
        if result["returncode"] == 0:
            test_passed = True
            logging.info("✓ 版本管理器检查功能通过")
        else:
            logging.error(f"✗ 版本管理器检查功能失败，命令返回码: {result['returncode']}, 错误信息: {result['stderr']}")
        
        self.test_results.append({
            "test_name": "version_manager",
            "test_target": "版本管理器检查功能",
            "status": "PASS" if test_passed else "FAIL",
            "details": result
        })
    
    def test_automated_workflow(self):
        """测试automated_workflow.py工具"""
        logging.info("=== 测试automated_workflow.py工具 ===")
        
        # 测试自动化工作流检查功能
        command = [
            PYTHON_PATH,
            os.path.join(AI_TOOLS_PATH, "集成管理工具", "automated_workflow.py"),
            "check",
            "--reason",
            "自动化测试",
            "--config",
            CONFIG_FILE,
            "--compiler",
            "autoshop"
        ]
        
        result = self.run_command(command)
        
        # 检查结果
        test_passed = False
        if result["returncode"] == 0:
            test_passed = True
            logging.info("✓ 自动化工作流检查功能通过")
        else:
            logging.error(f"✗ 自动化工作流检查功能失败，命令返回码: {result['returncode']}, 错误信息: {result['stderr']}")
        
        self.test_results.append({
            "test_name": "automated_workflow",
            "test_target": "自动化工作流检查功能",
            "status": "PASS" if test_passed else "FAIL",
            "details": result
        })
    
    def generate_test_report(self):
        """生成测试报告"""
        logging.info("=== 生成测试报告 ===")
        
        # 计算测试统计
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["status"] == "PASS")
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # 生成报告内容
        report_content = f"""# 自动化测试报告

## 报告信息

| 项目名称 | 单线圈气缸控制FB |
|---------|---------------|
| 测试时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| 测试时长 | {self.end_time - self.start_time:.2f}秒 |
| 测试工具 | Python {sys.version} |

## 测试统计

| 测试总数 | 通过测试 | 失败测试 | 通过率 |
|---------|---------|---------|-------|
| {total_tests} | {passed_tests} | {failed_tests} | {pass_rate:.2f}% |

## 测试详情

"""
        
        # 添加测试详情
        for i, test in enumerate(self.test_results, 1):
            report_content += f"### {i}. {test['test_name']} - {test['test_target']}\n\n"
            report_content += f"| 测试项 | 结果 |\n"
            report_content += f"|-------|------|\n"
            report_content += f"| 测试名称 | {test['test_name']} |\n"
            report_content += f"| 测试目标 | {test['test_target']} |\n"
            report_content += f"| 测试状态 | {test['status']} |\n\n"
            
            if test['status'] == "FAIL":
                report_content += f"#### 失败详情\n\n"
                report_content += f"```\n"
                report_content += f"返回码: {test['details']['returncode']}\n"
                report_content += f"标准输出: {test['details']['stdout']}\n"
                report_content += f"标准错误: {test['details']['stderr']}\n"
                report_content += f"```\n\n"
        
        # 写入报告文件
        report_file = os.path.join(PROJECT_ROOT, f"自动化测试报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        logging.info(f"✓ 测试报告生成完成: {report_file}")
        logging.info(f"测试结果: {passed_tests} 通过, {failed_tests} 失败, 通过率 {pass_rate:.2f}%")
    
    def run_all_tests(self):
        """运行所有测试"""
        logging.info("=== 开始自动化测试 ===")
        self.start_time = time.time()
        
        # 运行所有测试用例
        self.test_check_encoding()
        self.test_verify_csv_format()
        self.test_version_manager()
        self.test_automated_workflow()
        
        self.end_time = time.time()
        
        # 生成测试报告
        self.generate_test_report()
        logging.info("=== 自动化测试完成 ===")

if __name__ == "__main__":
    # 创建测试实例
    test = AutomationTest()
    # 运行所有测试
    test.run_all_tests()
