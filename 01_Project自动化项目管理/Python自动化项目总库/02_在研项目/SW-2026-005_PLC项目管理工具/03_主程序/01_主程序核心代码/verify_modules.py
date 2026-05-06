# -*- coding: utf-8 -*-
"""
快速验证脚本 - 验证所有新创建的模块可以正确导入和使用
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("开始验证检查器框架模块...")
print("=" * 60)

# 测试1: 导入基础模块
print("\n[1/6] 测试基础模块导入...")
try:
    from src.checkers.base_checker import BaseChecker, Severity, RuleInfo
    print("✓ src.checkers.base_checker 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

try:
    from src.checkers.rule_registry import RuleRegistry
    print("✓ src.checkers.rule_registry 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

try:
    from src.checkers import BaseChecker, RuleRegistry, Severity, RuleInfo
    print("✓ src.checkers 包导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试2: 数据模型导入
print("\n[2/6] 测试数据模型导入...")
try:
    from src.models.check_result import Violation, CheckResult, CheckReport
    print("✓ src.models.check_result 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试3: 解析器导入
print("\n[3/6] 测试解析器导入...")
try:
    from src.parsers.spec_doc_parser import SpecDocParser, SpecRule
    print("✓ src.parsers.spec_doc_parser 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试4: Severity枚举
print("\n[4/6] 测试Severity枚举...")
assert Severity.ERROR == 3, "ERROR值应为3"
assert Severity.WARNING == 2, "WARNING值应为2"
assert Severity.INFO == 1, "INFO值应为1"
print("✓ Severity枚举值正确")

# 测试5: RuleInfo数据类
print("\n[5/6] 测试RuleInfo数据类...")
info = RuleInfo(
    rule_id="TEST_001",
    name="测试规则",
    description="这是一个测试",
    category="test",
    severity=Severity.WARNING,
)
d = info.to_dict()
assert d["rule_id"] == "TEST_001"
assert d["severity"] == "WARNING"
print("✓ RuleInfo数据类工作正常")

# 测试6: Violation数据类
print("\n[6/6] 测试Violation数据类...")
violation = Violation(
    rule_id="VIOLATION_001",
    severity=Severity.ERROR,
    message="测试违规消息",
    file_path="/test/file.st",
    line_number=42,
    column=10,
    suggestion="建议修复方案",
)
str_repr = str(violation)
dict_repr = violation.to_dict()
assert "[ERROR]" in str_repr
assert dict_repr["line_number"] == 42
assert violation.location_str == "file.st:42:10"
print("✓ Violation数据类工作正常")

# 测试7: CheckResult数据类
print("\n[额外测试] 测试CheckResult数据类...")
result = CheckResult(source_file="test.st")
result.add_violation(Violation(
    rule_id="R1", severity=Severity.ERROR, message="错误1"
))
result.add_violation(Violation(
    rule_id="R2", severity=Severity.WARNING, message="警告1"
))
assert result.total_violations == 2
assert result.error_count == 1
assert result.warning_count == 1
assert result.has_errors is True
assert result.is_passed is False
print("✓ CheckResult数据类工作正常")

# 测试8: CheckReport数据类
print("\n[额外测试] 测试CheckReport数据类...")
report = CheckReport(project_name="测试项目")
report.add_result(result)
assert report.total_files_checked == 1
assert report.total_errors == 1
assert report.quality_score < 100
summary = report.generate_summary_text()
assert "测试项目" in summary
print("✓ CheckReport数据类工作正常")

# 测试9: RuleRegistry单例
print("\n[额外测试] 测试RuleRegistry单例...")
RuleRegistry.reset_instance()  # 确保干净状态
registry = RuleRegistry.get_instance()
registry2 = RuleRegistry.get_instance()
assert registry is registry2, "单例模式失效"
print("✓ RuleRegistry单例模式正常")

# 测试10: SpecDocParser基本功能
print("\n[额外测试] 测试SpecDocParser...")
import tempfile
import os

spec_content = """# 测试规范

### [TEST-001] 规则一
**优先级**: high
**严重级别**: error
**类别**: test

这是规则一的详细内容。

### [TEST-002] 规则二
**优先级**: medium
**严重级别**: warning

规则二的内容。
"""

parser = SpecDocParser()
with tempfile.NamedTemporaryFile(
    mode='w', suffix='.md', encoding='utf-8', delete=False
) as f:
    f.write(spec_content)
    temp_file = f.name

try:
    rules = parser.parse_file(temp_file)
    assert len(rules) == 2, f"应解析出2条规则，实际: {len(rules)}"
    assert rules[0].rule_id == "TEST-001"
    assert rules[0].priority == "high"
    assert rules[0].severity == "error"
    assert "详细内容" in rules[0].content
    print("✓ SpecDocParser解析功能正常")
finally:
    os.unlink(temp_file)

# 完成
print("\n" + "=" * 60)
print("✅ 所有模块验证通过！")
print("=" * 60)
print("\n已创建的文件:")
files = [
    "src/checkers/__init__.py",
    "src/checkers/base_checker.py",
    "src/checkers/rule_registry.py",
    "src/models/check_result.py",
    "src/parsers/spec_doc_parser.py",
    "tests/test_checker_framework.py",
]
for f in files:
    full_path = Path(__file__).parent / f
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"  ✓ {f} ({size:,} bytes)")
    else:
        print(f"  ✗ {f} (不存在)")
