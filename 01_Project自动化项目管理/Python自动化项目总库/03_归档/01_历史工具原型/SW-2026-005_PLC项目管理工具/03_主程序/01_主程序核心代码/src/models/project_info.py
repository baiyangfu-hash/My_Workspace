"""项目概览卡片数据模型 - 来源：立项表"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RiskItem:
    """风险评估条目"""
    risk_item: str = "待补充"
    level: str = "待补充"
    measure: str = "待补充"


@dataclass
class ProjectInfo:
    """项目概览卡片数据 - 来源：立项表"""

    # 标识
    project_id: str = ""
    project_path: str = ""

    # §3 业务身份
    name: str = "待补充"
    business_desc: str = "待补充"
    important_note: str = "待补充"
    process_scope: str = "待补充"
    customer: str = "待补充"

    # §4 技术环境
    platform: str = "待补充"
    plc_model: str = "待补充"
    hmi_model: str = "待补充"
    driver: str = "待补充"
    communication: str = "待补充"
    # §4 控制参数
    axes: str = "待补充"
    precision: str = "待补充"
    safety_protection: str = "待补充"

    # §5 工程规模
    module_count: str = "待补充"
    module_names: str = "待补充"
    project_scope: str = "待补充"

    # §6 工程状态
    phase: str = "待补充"
    start_date: str = "待补充"
    end_date: str = "待补充"
    duration_days: str = "待补充"

    # §7 变更台账（从变更管理文件夹扫描）
    change_count: int = 0
    pending_change_count: int = 0

    # 附录A
    team: str = "待补充"
    risks: list[RiskItem] = field(default_factory=list)

    # 元数据
    proj_file_path: str = ""
    proj_file_mtime: float = 0.0
