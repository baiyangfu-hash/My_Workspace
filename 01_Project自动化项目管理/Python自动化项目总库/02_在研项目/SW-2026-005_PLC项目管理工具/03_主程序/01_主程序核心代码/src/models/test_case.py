"""
测试用例数据模型模块

本模块定义了PLC测试用例的数据结构，包括：
- TestStep: 测试步骤（SET/WAIT/ASSERT三种类型）
- TestCase: 单个测试用例
- TestSuite: 测试套件（包含多个测试用例）

设计原则：
- 使用dataclass实现不可变数据类
- 支持类型注解和验证
- 提供序列化/反序列化能力
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Any, Dict
from pathlib import Path


class StepType(Enum):
    """测试步骤类型枚举"""
    SET = auto()          # 设置变量值
    WAIT_CYCLES = auto()  # 等待扫描周期
    ASSERT = auto()       # 断言验证


@dataclass(frozen=True)
class TestStep:
    """
    测试步骤数据类

    表示测试用例中的单个操作步骤，支持三种类型：
    - SET: 设置变量的值（如 SET GlobalVars.x := TRUE;）
    - WAIT_CYCLES: 等待指定数量的PLC扫描周期（如 WAIT_CYCLES 100;）
    - ASSERT: 断言变量的预期值（如 ASSERT GlobalVars.y = FALSE;）

    Attributes:
        step_type: 步骤类型（SET/WAIT_CYCLES/ASSERT）
        variable: 变量名（SET和ASSERT类型使用）
        value: 设定值或期望值（SET和ASSERT类型使用）
        cycles: 等待周期数（WAIT_CYCLES类型使用）
        raw_line: 原始语句行（用于调试和错误定位）
        line_number: 行号（用于错误报告）
    """
    step_type: StepType
    variable: Optional[str] = None
    value: Any = None
    cycles: Optional[int] = None
    raw_line: str = ""
    line_number: int = 0

    def __post_init__(self):
        """初始化后验证数据完整性"""
        if self.step_type == StepType.SET:
            if not self.variable:
                raise ValueError("SET步骤必须指定变量名")
        elif self.step_type == StepType.WAIT_CYCLES:
            if self.cycles is None or self.cycles < 0:
                raise ValueError("WAIT_CYCLES步骤必须指定非负周期数")
        elif self.step_type == StepType.ASSERT:
            if not self.variable:
                raise ValueError("ASSERT步骤必须指定变量名")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'step_type': self.step_type.name,
            'raw_line': self.raw_line,
            'line_number': self.line_number
        }
        if self.step_type in (StepType.SET, StepType.ASSERT):
            result['variable'] = self.variable
            result['value'] = self.value
        elif self.step_type == StepType.WAIT_CYCLES:
            result['cycles'] = self.cycles
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestStep':
        """从字典创建实例"""
        step_type = StepType[data['step_type']]
        return cls(
            step_type=step_type,
            variable=data.get('variable'),
            value=data.get('value'),
            cycles=data.get('cycles'),
            raw_line=data.get('raw_line', ''),
            line_number=data.get('line_number', 0)
        )

    def __str__(self) -> str:
        """人类可读的字符串表示"""
        if self.step_type == StepType.SET:
            return f"SET {self.variable} := {self.value}"
        elif self.step_type == StepType.WAIT_CYCLES:
            return f"WAIT_CYCLES {self.cycles}"
        elif self.step_type == StepType.ASSERT:
            return f"ASSERT {self.variable} = {self.value}"
        return f"Unknown step: {self.raw_line}"


@dataclass
class TestCase:
    """
    测试用例数据类

    表示一个完整的PLC测试用例，包含名称、描述和一系列测试步骤。

    Attributes:
        name: 测试用例名称（来自TEST_CASE声明）
        description: 测试用例描述（从注释中提取）
        steps: 测试步骤列表
        file_path: 源文件路径
        start_line: 起始行号
        end_line: 结束行号
    """
    name: str
    description: str = ""
    steps: List[TestStep] = field(default_factory=list)
    file_path: Optional[Path] = None
    start_line: int = 0
    end_line: int = 0

    @property
    def step_count(self) -> int:
        """返回步骤总数"""
        return len(self.steps)

    @property
    def has_set_steps(self) -> bool:
        """是否包含SET步骤"""
        return any(s.step_type == StepType.SET for s in self.steps)

    @property
    def has_assert_steps(self) -> bool:
        """是否包含ASSERT步骤"""
        return any(s.step_type == StepType.ASSERT for s in self.steps)

    @property
    def total_wait_cycles(self) -> int:
        """计算总等待周期数"""
        return sum(
            (s.cycles or 0) for s in self.steps
            if s.step_type == StepType.WAIT_CYCLES
        )

    def get_steps_by_type(self, step_type: StepType) -> List[TestStep]:
        """按类型获取步骤"""
        return [s for s in self.steps if s.step_type == step_type]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps],
            'file_path': str(self.file_path) if self.file_path else None,
            'start_line': self.start_line,
            'end_line': self.end_line
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """从字典创建实例"""
        return cls(
            name=data['name'],
            description=data.get('description', ''),
            steps=[TestStep.from_dict(s) for s in data.get('steps', [])],
            file_path=Path(data['file_path']) if data.get('file_path') else None,
            start_line=data.get('start_line', 0),
            end_line=data.get('end_line', 0)
        )

    def __str__(self) -> str:
        """简短描述"""
        return f"TestCase '{self.name}' ({self.step_count} steps)"

    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"TestCase(name='{self.name}', "
            f"steps={self.step_count}, "
            f"file={self.file_path})"
        )


@dataclass
class TestSuite:
    """
    测试套件数据类

    表示一个SCLTest文件中包含的所有测试用例集合。

    Attributes:
        file_path: SCLTest文件路径
        test_cases: 测试用例列表
        header_comments: 文件头注释
        parse_errors: 解析过程中的错误信息
    """
    file_path: Path
    test_cases: List[TestCase] = field(default_factory=list)
    header_comments: List[str] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)

    @property
    def test_case_count(self) -> int:
        """返回测试用例总数"""
        return len(self.test_cases)

    @property
    def total_steps(self) -> int:
        """返回所有测试用例的步骤总数"""
        return sum(tc.step_count for tc in self.test_cases)

    @property
    def total_wait_cycles(self) -> int:
        """计算所有测试用例的总等待周期数"""
        return sum(tc.total_wait_cycles for tc in self.test_cases)

    @property
    def has_errors(self) -> bool:
        """是否存在解析错误"""
        return len(self.parse_errors) > 0

    def get_test_case_by_name(self, name: str) -> Optional[TestCase]:
        """按名称查找测试用例"""
        for tc in self.test_cases:
            if tc.name == name:
                return tc
        return None

    def get_all_variable_names(self) -> set:
        """提取所有涉及的变量名"""
        variables = set()
        for tc in self.test_cases:
            for step in tc.steps:
                if step.variable:
                    variables.add(step.variable)
        return variables

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'file_path': str(self.file_path),
            'test_cases': [tc.to_dict() for tc in self.test_cases],
            'header_comments': self.header_comments,
            'parse_errors': self.parse_errors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestSuite':
        """从字典创建实例"""
        return cls(
            file_path=Path(data['file_path']),
            test_cases=[TestCase.from_dict(tc) for tc in data.get('test_cases', [])],
            header_comments=data.get('header_comments', []),
            parse_errors=data.get('parse_errors', [])
        )

    def __str__(self) -> str:
        """简短描述"""
        return f"TestSuite '{self.file_path.name}' ({self.test_case_count} cases)"

    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"TestSuite(file='{self.file_path.name}', "
            f"cases={self.test_case_count}, "
            f"total_steps={self.total_steps}, "
            f"errors={len(self.parse_errors)})"
        )
