# -*- coding: utf-8 -*-
"""
GUI测试运行入口
运行所有GUI测试并生成综合报告
"""
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication

app = None

def get_app():
    global app
    if app is None:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    return app


def run_all_tests():
    from tests.test_gui import GUITestRunner, generate_report as generate_basic_report
    from tests.test_gui_functional import FunctionalTestRunner, generate_functional_report
    
    print("\n" + "=" * 70)
    print(" " * 20 + "Python项目管理工具 GUI自动化测试套件")
    print("=" * 70)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    all_results = []
    total_start = datetime.now()
    
    print("\n" + "-" * 70)
    print("第一阶段: GUI基础测试 (控件存在性、属性验证)")
    print("-" * 70)
    
    basic_runner = GUITestRunner()
    basic_result = basic_runner.run_all_tests()
    basic_report = generate_basic_report(basic_result)
    all_results.extend(basic_result.to_dict()['test_cases'])
    
    print(f"\n基础测试完成，报告: {basic_report}")
    
    print("\n" + "-" * 70)
    print("第二阶段: GUI功能测试 (交互操作、功能验证)")
    print("-" * 70)
    
    functional_runner = FunctionalTestRunner()
    functional_results = functional_runner.run_all_tests()
    functional_report = generate_functional_report(
        functional_results, 
        functional_runner.start_time, 
        functional_runner.end_time
    )
    all_results.extend(functional_results)
    
    print(f"\n功能测试完成，报告: {functional_report}")
    
    total_end = datetime.now()
    
    total = len(all_results)
    passed = sum(1 for r in all_results if r['status'] == 'PASS')
    failed = sum(1 for r in all_results if r['status'] == 'FAIL')
    errors = sum(1 for r in all_results if r['status'] == 'ERROR')
    
    print("\n" + "=" * 70)
    print(" " * 25 + "测试执行汇总")
    print("=" * 70)
    print(f"测试总耗时: {str(total_end - total_start).split('.')[0]}")
    print(f"测试用例总数: {total}")
    print(f"  ✅ 通过: {passed}")
    print(f"  ❌ 失败: {failed}")
    print(f"  ⚠️  错误: {errors}")
    print(f"通过率: {round(passed/total*100, 2) if total > 0 else 0}%")
    print("=" * 70)
    
    generate_summary_report(all_results, total_start, total_end, basic_report, functional_report)
    
    return all_results


def generate_summary_report(results, start_time, end_time, basic_report, functional_report):
    report_dir = Path(__file__).parent.parent / "data" / "test_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"GUI测试汇总报告_{timestamp}.md"
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    modules = {}
    for r in results:
        if r['module'] not in modules:
            modules[r['module']] = {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0}
        modules[r['module']]['total'] += 1
        if r['status'] == 'PASS':
            modules[r['module']]['passed'] += 1
        elif r['status'] == 'FAIL':
            modules[r['module']]['failed'] += 1
        else:
            modules[r['module']]['errors'] += 1
    
    content = f"""# GUI自动化测试汇总报告

## 测试概要

| 项目 | 值 |
|------|-----|
| 测试时间 | {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')} |
| 测试耗时 | {str(end_time - start_time).split('.')[0]} |
| 测试用例总数 | {total} |
| 通过数量 | {passed} |
| 失败数量 | {failed} |
| 错误数量 | {errors} |
| 通过率 | {round(passed/total*100, 2) if total > 0 else 0}% |

## 测试结果可视化

```
通过率: {round(passed/total*100, 1) if total > 0 else 0}%
{'█' * passed}{'░' * (total - passed)} 

通过: {passed} | 失败: {failed} | 错误: {errors}
```

## 模块测试统计

| 模块 | 总数 | 通过 | 失败 | 错误 | 通过率 |
|------|------|------|------|------|--------|
"""
    
    for mod, stats in modules.items():
        rate = round(stats['passed']/stats['total']*100, 2) if stats['total'] > 0 else 0
        status = "✅" if rate == 100 else ("⚠️" if rate >= 80 else "❌")
        content += f"| {mod} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {rate}% {status} |\n"
    
    content += f"""
## 测试阶段

### 第一阶段: 基础测试
- 测试目标: 验证GUI控件存在性、属性正确性
- 详细报告: `{Path(basic_report).name}`

### 第二阶段: 功能测试  
- 测试目标: 验证GUI交互操作、功能正确性
- 详细报告: `{Path(functional_report).name}`

## 失败/错误用例详情

"""
    
    failed_cases = [r for r in results if r['status'] != 'PASS']
    if failed_cases:
        for r in failed_cases:
            status_icon = "❌" if r['status'] == 'FAIL' else "⚠️"
            content += f"{status_icon} **{r['module']}** - {r['test_name']}\n"
            content += f"   - 状态: {r['status']}\n"
            content += f"   - 信息: {r['message']}\n\n"
    else:
        content += "所有测试用例均通过！🎉\n"
    
    content += f"""
## 测试环境

| 项目 | 值 |
|------|-----|
| 操作系统 | {os.name} |
| Python版本 | {sys.version.split()[0]} |
| PyQt5版本 | {__import__('PyQt5.QtCore').QtCore.PYQT_VERSION_STR} |

## 测试结论

本次GUI自动化测试共执行 **{total}** 个测试用例:

- ✅ **通过**: {passed} 个 ({round(passed/total*100, 2) if total > 0 else 0}%)
- ❌ **失败**: {failed} 个 ({round(failed/total*100, 2) if total > 0 else 0}%)
- ⚠️ **错误**: {errors} 个 ({round(errors/total*100, 2) if total > 0 else 0}%)

"""
    
    if passed == total:
        content += "**测试结论**: 所有测试用例通过，GUI功能正常！ ✅\n"
    elif passed / total >= 0.9:
        content += "**测试结论**: 大部分测试通过，存在少量问题需要关注。 ⚠️\n"
    else:
        content += "**测试结论**: 存在较多问题，建议进行修复后重新测试。 ❌\n"
    
    content += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n汇总报告已生成: {report_file}")
    return report_file


if __name__ == "__main__":
    get_app()
    run_all_tests()
