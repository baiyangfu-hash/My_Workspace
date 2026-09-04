"""PLC 项目初始化与结构检查 Service

遵循 LSP-907 V1.0.0 项目配置规范，提供：
- init: 创建标准 PLC 项目目录骨架和模板文件
- check: 验证项目结构是否符合 LSP-907 规范
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime

from src.utils.file_utils import write_file
from src.utils.logger import get_logger

log = get_logger(__name__)


# ── 常量 ──────────────────────────────────────────────────

# 标准 PLC 项目目录结构（LSP-907 §3.1）
STD_DIRS = [
    "02_PLC程序/通用ST程序及变量表",
    "03_HMI设计",
    "04_现场调试",
    "04_变更管理",
    "PRD",
]

# PRD 文档模板集（LSP-907 + SysLib FB 标准）
STD_PRDS = [
    "需求分析文档_REQ.md",
    "接口文档_INT.md",
    "详细设计说明书_DSN.md",
    "技术方案文档_TEC.md",
]

# .plc.json 必填字段（LSP-907 §1.1）
REQUIRED_PLC_JSON_FIELDS = ["name", "description", "version"]

# 允许缺失 .plc.json 的库类型（SysLib FB 项目无 .plc.json）
SKIP_PLC_JSON_TYPES = ["syslib_fb"]

# V9: PRD 文档命名规范映射（标准名 → 非标准匹配模式）
# 用于 standardize_docs() 检测并修正非标准命名
NAMING_RULES: dict[str, dict] = {
    "需求分析文档_REQ.md": {
        "doc_type": "REQ",
        "prefix": "需求",
        "patterns": [r"^需求文档_PRD-.*\.md$", r"^.*_REQ\.md$"],
    },
    "接口文档_INT.md": {
        "doc_type": "INT",
        "prefix": "接口",
        "patterns": [r"^接口文档_IFC-.*\.md$", r"^.*_INT\.md$"],
    },
    "详细设计说明书_DSN.md": {
        "doc_type": "DSN",
        "prefix": "详细设计",
        "patterns": [r"^详细设计说明书_DSN-.*\.md$", r"^.*_DSN\.md$"],
    },
    "技术方案文档_TEC.md": {
        "doc_type": "TEC",
        "prefix": "技术方案",
        "patterns": [r"^技术方案文档_TEC-.*\.md$", r"^.*_TEC\.md$"],
    },
}


# ── 数据模型 ──────────────────────────────────────────────

@dataclass
class CheckItem:
    """单条检查项"""
    item: str           # 检查项名称
    status: str         # "pass" / "warn" / "fail"
    message: str        # 详细说明


@dataclass
class CheckResult:
    """结构检查结果"""
    project_path: str
    project_type: str = "standard"  # "standard" / "syslib_fb"
    items: list[CheckItem] = field(default_factory=list)
    pass_count: int = 0
    warn_count: int = 0
    fail_count: int = 0

    def add(self, item: str, status: str, message: str) -> None:
        self.items.append(CheckItem(item, status, message))
        if status == "pass":
            self.pass_count += 1
        elif status == "warn":
            self.warn_count += 1
        else:
            self.fail_count += 1

    @property
    def all_pass(self) -> bool:
        return self.fail_count == 0


# ── V9 新增数据结构 ──────────────────────────────────────

@dataclass
class RepairAction:
    """单条修复动作"""
    item: str           # 修复项名称
    action: str         # 修复动作描述
    destructive: bool   # 是否破坏性操作
    status: str         # "fixed" / "skipped" / "failed"
    detail: str         # 详细说明


@dataclass
class RepairResult:
    """自动修复结果"""
    project_path: str
    actions: list[RepairAction] = field(default_factory=list)
    fixed_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    before_check: CheckResult | None = None
    after_check: CheckResult | None = None

    def add(self, item: str, action: str, destructive: bool,
            status: str, detail: str) -> None:
        self.actions.append(RepairAction(item, action, destructive, status, detail))
        if status == "fixed":
            self.fixed_count += 1
        elif status == "skipped":
            self.skipped_count += 1
        else:
            self.failed_count += 1


@dataclass
class RenamePlan:
    """文档重命名计划"""
    old_path: str       # 原文件路径
    new_path: str       # 新文件路径
    doc_type: str       # "REQ" / "INT" / "DSN" / "TEC"
    applied: bool = False       # 是否已执行
    backup_path: str = ""       # 备份路径（.bak）


@dataclass
class StandardizeResult:
    """文档标准化结果"""
    project_path: str
    plans: list[RenamePlan] = field(default_factory=list)
    applied_count: int = 0
    skipped_count: int = 0
    reference_updates: list[str] = field(default_factory=list)


# ── 模板内容 ──────────────────────────────────────────────

def _plc_json_template(project_id: str, description: str, version: str = "V1.0.0") -> str:
    """生成 .plc.json 模板（LSP-907 §1.1）"""
    return json.dumps({
        "name": project_id,
        "description": description,
        "version": version,
        "libraries": [
            "../../../01_SharedLibraries/SysLib"
        ],
    }, indent=2, ensure_ascii=False) + "\n"


def _pm_session_template(project_id: str, project_name: str, project_root: str) -> str:
    """生成 PM_SESSION 模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""# PM_SESSION_{project_id}

## 0. Meta
- project_id: {project_id}
- project_name: {project_name}
- project_root: {project_root}
- last_updated: {today}
- owners: 待填写

## 1. Positioning（项目定位）
- one_liner: 待填写
- users: 待填写
- non_goals: 待填写

## 2. Current Focus（当前焦点）
- current_focus: 项目初始化
- milestone: V1.0.0
- acceptance: 待定义

## 3. Status Summary（当前状态摘要）
- in_progress:
  - 项目骨架搭建
- next_up:
  - 需求分析
- open_questions:
  - 待整理
- risks_dependencies:
  - 待评估
- spec_compliance:
  - last_check: {today}
  - result: 待检查

## 4. Artifacts Index（文档索引）
- req: PRD/需求分析文档_REQ.md
- int: PRD/接口文档_INT.md
- dsn: PRD/详细设计说明书_DSN.md
- tec: PRD/技术方案文档_TEC.md

## 5. Logs（按事件沉淀）
- change_log:
  - {today} 项目初始化，骨架创建

## 6. Implementation Log
- {today} | skill=pm-workflow | mode=项目初始化
  - goal: 创建标准 PLC 项目骨架
  - changed_files: 全部模板文件
  - impact: 项目可开始需求分析和编码
  - risks: 无
"""


def _req_template(project_id: str, project_name: str) -> str:
    """生成 REQ 需求分析文档模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""---
spec_id: REQ-{project_id}
title: "{project_id}需求分析文档"
version: "V1.0.0"
domain: plc
lifecycle: draft
tags: ["需求分析"]
---

# 需求分析文档 {project_id}

## 1. 文档基础信息

**文档标题**：{project_id}需求分析文档
**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：待填写
**审核人**：待填写
**遵循规范**：LSP-905, LSP-904, LSP-903

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 | 详细说明 |
|--------|----------|--------|----------|----------|
| V1.0.0 | 初始创建 | 待填写 | {today} | 项目初始化 |

## 3. 项目背景

### 3.1 项目来源
待填写

### 3.2 业务目标
待填写

## 4. 功能需求

### 4.1 核心功能
待填写

### 4.2 非功能需求
待填写

## 5. 接口需求
待填写

## 6. 约束条件
待填写
"""


def _int_template(project_id: str, project_name: str) -> str:
    """生成 INT 接口文档模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""---
spec_id: INT-{project_id}
title: "{project_id}接口文档"
version: "V1.0.0"
domain: plc
lifecycle: draft
tags: ["接口文档"]
---

# 接口文档 {project_id}

## 1. 文档基础信息

**文档标题**：{project_id}接口文档
**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：待填写
**遵循规范**：INT-815

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V1.0.0 | 初始创建 | 待填写 | {today} |

## 3. 功能块接口

### 3.1 FB_xxx

| 方向 | 参数名 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| VAR_INPUT | 待填写 | 待填写 | 待填写 | 待填写 |
| VAR_OUTPUT | 待填写 | 待填写 | 待填写 | 待填写 |

## 4. 结构体定义

### 4.1 ST_xxx

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| 待填写 | 待填写 | 待填写 | 待填写 |
"""


def _dsn_template(project_id: str, project_name: str) -> str:
    """生成 DSN 详细设计文档模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""---
spec_id: DSN-{project_id}
title: "{project_id}详细设计说明书"
version: "V1.0.0"
domain: plc
lifecycle: draft
tags: ["详细设计"]
---

# 详细设计说明书 {project_id}

## 1. 文档基础信息

**文档标题**：{project_id}详细设计说明书
**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：待填写
**遵循规范**：LSP-905, PLC-023

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V1.0.0 | 初始创建 | 待填写 | {today} |

## 3. 架构设计

### 3.1 系统架构
待填写

### 3.2 模块划分
待填写

## 4. 状态机设计
待填写

## 5. 定时器设计
待填写

## 6. 报警设计
待填写
"""


def _tec_template(project_id: str, project_name: str) -> str:
    """生成 TEC 技术方案文档模板"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""---
spec_id: TEC-{project_id}
title: "{project_id}技术方案文档"
version: "V1.0.0"
domain: plc
lifecycle: draft
tags: ["技术方案"]
---

# 技术方案文档 {project_id}

## 1. 文档基础信息

**文档标题**：{project_id}技术方案文档
**文档版本**：V1.0.0
**编制日期**：{today}
**编制人**：待填写
**遵循规范**：LSP-907

## 2. 版本变更记录

| 版本号 | 变更内容 | 变更人 | 变更日期 |
|--------|----------|--------|----------|
| V1.0.0 | 初始创建 | 待填写 | {today} |

## 3. 技术选型

### 3.1 编程平台
待填写

### 3.2 PLC 型号
待填写

### 3.3 依赖库
- SysLib (共享库)

## 4. 控制方案
待填写

## 5. 安全方案
待填写
"""


# ── Service ───────────────────────────────────────────────

class PlcProjectService:
    """PLC 项目初始化与结构检查 Service"""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = workspace_root

    # ── 项目初始化 ────────────────────────────────────────

    def init_project(
        self,
        project_id: str,
        project_name: str,
        description: str = "",
        dry_run: bool = False,
    ) -> dict:
        """创建标准 PLC 项目骨架

        Args:
            project_id: 项目编号，如 DJ-2026-010
            project_name: 项目名称，如 边框缓存机
            description: 项目描述（可选，默认使用 project_name）
            dry_run: 仅预览，不实际创建文件

        Returns:
            {
                "project_id": str,
                "project_path": str,
                "created_files": [str, ...],
                "dry_run": bool,
            }
        """
        if not description:
            description = project_name

        project_dir = f"{project_id}_{project_name}"
        project_path = os.path.join(self.workspace_root, project_dir)

        created: list[str] = []

        if dry_run:
            log.info("[DRY-RUN] 将创建项目: %s", project_path)

        # 1. 项目根目录
        self._mkdir(project_path, dry_run)
        created.append(f"{project_dir}/")

        # 2. .plc.json（项目根）
        plc_json = _plc_json_template(project_id, description)
        self._write(os.path.join(project_path, ".plc.json"), plc_json, dry_run)
        created.append(f"{project_dir}/.plc.json")

        # 3. PM_SESSION
        pm_session = _pm_session_template(project_id, project_name, project_path)
        self._write(
            os.path.join(project_path, f"PM_SESSION_{project_id}.md"),
            pm_session,
            dry_run,
        )
        created.append(f"{project_dir}/PM_SESSION_{project_id}.md")

        # 4. 标准目录
        for d in STD_DIRS:
            self._mkdir(os.path.join(project_path, d), dry_run)
            created.append(f"{project_dir}/{d}/")

        # 5. 子 .plc.json（02_PLC程序/通用ST程序及变量表/）
        sub_plc_json = _plc_json_template(project_id, f"{description} PLC程序")
        self._write(
            os.path.join(project_path, "02_PLC程序", "通用ST程序及变量表", ".plc.json"),
            sub_plc_json,
            dry_run,
        )
        created.append(f"{project_dir}/02_PLC程序/通用ST程序及变量表/.plc.json")

        # 6. PRD 文档模板
        prd_path = os.path.join(project_path, "PRD")
        templates = [
            ("需求分析文档_REQ.md", _req_template(project_id, project_name)),
            ("接口文档_INT.md", _int_template(project_id, project_name)),
            ("详细设计说明书_DSN.md", _dsn_template(project_id, project_name)),
            ("技术方案文档_TEC.md", _tec_template(project_id, project_name)),
        ]
        for filename, content in templates:
            self._write(os.path.join(prd_path, filename), content, dry_run)
            created.append(f"{project_dir}/PRD/{filename}")

        log.info("项目初始化完成: %s (%d 个文件/目录)", project_id, len(created))
        return {
            "project_id": project_id,
            "project_path": project_path,
            "created_files": created,
            "dry_run": dry_run,
        }

    # ── 结构检查 ──────────────────────────────────────────

    def check_project(self, project_path: str) -> CheckResult:
        """检查项目结构是否符合 LSP-907 规范

        Args:
            project_path: 项目根目录绝对路径

        Returns:
            CheckResult: 检查结果，包含所有检查项及其状态
        """
        result = CheckResult(project_path=project_path)

        # 检测项目类型
        project_type = self._detect_project_type(project_path)
        result.project_type = project_type

        # 1. 检查 .plc.json
        self._check_plc_json(project_path, result)

        # 2. 检查 PM_SESSION
        self._check_pm_session(project_path, result)

        # 3. 检查 PRD 文档
        self._check_prd_docs(project_path, result)

        # 4. 检查目录结构
        if project_type == "standard":
            self._check_directory_structure(project_path, result)

        log.info(
            "项目检查完成: %s - pass=%d warn=%d fail=%d",
            os.path.basename(project_path),
            result.pass_count,
            result.warn_count,
            result.fail_count,
        )
        return result

    def check_workspace(self, scan_depth: int = 4) -> list[CheckResult]:
        """扫描工作空间下所有项目并逐一检查

        Args:
            scan_depth: 扫描深度（默认4层，覆盖 SysLib/actuator/FB_xxx 三级嵌套）

        Returns:
            所有项目的检查结果列表
        """
        results: list[CheckResult] = []
        self._scan_and_check(self.workspace_root, results, depth=0, max_depth=scan_depth)
        return results

    # ── V9: 自动修复 ──────────────────────────────────────

    def repair_project(
        self,
        project_path: str,
        dry_run: bool = False,
        rename_confirm: bool = False,
    ) -> RepairResult:
        """自动修复项目结构问题

        修复规则：
        - 非破坏性操作（创建目录/文件/补全字段）：自动执行
        - 破坏性操作（文件重命名）：需 rename_confirm=True 才执行

        Args:
            project_path: 项目根目录绝对路径
            dry_run: 仅预览不执行
            rename_confirm: 是否确认文件重命名（破坏性操作）

        Returns:
            RepairResult: 修复结果
        """
        log.info("开始修复项目: %s (dry_run=%s, rename_confirm=%s)",
                 project_path, dry_run, rename_confirm)

        result = RepairResult(project_path=project_path)

        # 1. 修复前检查
        result.before_check = self.check_project(project_path)

        project_id = self._resolve_project_id(project_path)
        project_name = os.path.basename(project_path)

        # 2. 遍历检查项，对 FAIL 项执行修复
        for item in result.before_check.items:
            if item.status != "fail":
                continue

            # 根据检查项名称路由到对应修复逻辑
            if item.item == ".plc.json":
                self._repair_plc_json(project_path, project_id, project_name,
                                      result, dry_run)
            elif item.item == "PM_SESSION":
                self._repair_pm_session(project_path, project_id, project_name,
                                        result, dry_run)
            elif item.item == "PRD 目录":
                self._repair_prd_dir(project_path, project_id, project_name,
                                     result, dry_run)
            elif item.item.startswith("PRD/"):
                # PRD/REQ.md 等文档缺失
                doc_name = item.item.split("/", 1)[1]
                self._repair_prd_doc(project_path, project_id, project_name,
                                     doc_name, result, dry_run)
            elif item.item.startswith("目录 "):
                # LSP-907 标准目录缺失
                dir_name = item.item.split(" ", 1)[1]
                self._repair_std_dir(project_path, dir_name, result, dry_run)

        # 3. 处理 WARN 项中的命名不匹配（破坏性操作）
        if rename_confirm:
            for item in result.before_check.items:
                if item.status != "warn":
                    continue
                if "命名不匹配" in item.message or "命名不规范" in item.message:
                    self._repair_rename(project_path, item, result, dry_run)
        else:
            # 未确认重命名，记录跳过
            for item in result.before_check.items:
                if item.status == "warn" and ("命名不匹配" in item.message or "命名不规范" in item.message):
                    result.add(
                        item=item.item,
                        action="重命名文件（需确认）",
                        destructive=True,
                        status="skipped",
                        detail=f"未确认重命名，跳过: {item.message}",
                    )

        # 4. 修复后重新检查
        if not dry_run:
            result.after_check = self.check_project(project_path)
        else:
            result.after_check = result.before_check

        log.info("修复完成: %s - fixed=%d skipped=%d failed=%d",
                 os.path.basename(project_path),
                 result.fixed_count, result.skipped_count, result.failed_count)
        return result

    def repair_workspace(
        self, dry_run: bool = False, rename_confirm: bool = False
    ) -> list[RepairResult]:
        """批量修复工作空间所有项目

        Args:
            dry_run: 仅预览不执行
            rename_confirm: 是否确认文件重命名

        Returns:
            所有项目的修复结果列表
        """
        results: list[RepairResult] = []
        check_results = self.check_workspace()
        for cr in check_results:
            if cr.all_pass:
                continue  # 跳过已通过的项目
            results.append(self.repair_project(cr.project_path, dry_run, rename_confirm))
        return results

    # ── V9: 文档标准化 ────────────────────────────────────

    def standardize_docs(
        self, project_path: str, apply: bool = False
    ) -> StandardizeResult:
        """检测并修正PRD文档命名

        Args:
            project_path: 项目根目录绝对路径
            apply: False=仅检测预览, True=执行重命名

        Returns:
            StandardizeResult: 标准化结果
        """
        log.info("开始标准化文档: %s (apply=%s)", project_path, apply)

        result = StandardizeResult(project_path=project_path)
        prd_path = os.path.join(project_path, "PRD")

        if not os.path.isdir(prd_path):
            log.warning("PRD 目录不存在，跳过标准化: %s", prd_path)
            return result

        # 扫描 PRD 目录下所有 .md 文件
        try:
            existing_files = [f for f in os.listdir(prd_path) if f.endswith(".md")]
        except OSError as e:
            log.error("扫描 PRD 目录失败: %s", e)
            return result

        # 对每个文件匹配命名规范
        for filename in existing_files:
            # 跳过已是标准命名的文件
            if filename in NAMING_RULES:
                continue

            # 匹配非标准命名模式
            for std_name, rule in NAMING_RULES.items():
                matched = any(re.search(p, filename) for p in rule["patterns"])
                if matched:
                    old_path = os.path.join(prd_path, filename)
                    new_path = os.path.join(prd_path, std_name)
                    plan = RenamePlan(
                        old_path=old_path,
                        new_path=new_path,
                        doc_type=rule["doc_type"],
                    )

                    if apply:
                        try:
                            # 备份原文件
                            backup_path = old_path + ".bak"
                            shutil.copy2(old_path, backup_path)
                            plan.backup_path = backup_path

                            # 执行重命名
                            os.rename(old_path, new_path)
                            plan.applied = True
                            result.applied_count += 1

                            # 更新关联引用
                            updates = self._update_references(
                                prd_path, filename, std_name
                            )
                            result.reference_updates.extend(updates)

                            log.info("重命名: %s → %s", filename, std_name)
                        except OSError as e:
                            log.error("重命名失败: %s → %s: %s",
                                      filename, std_name, e)
                            result.skipped_count += 1
                    else:
                        result.skipped_count += 1

                    result.plans.append(plan)
                    break  # 匹配到一个规则后不再继续匹配

        log.info("标准化完成: %s - applied=%d skipped=%d",
                 os.path.basename(project_path),
                 result.applied_count, result.skipped_count)
        return result

    def standardize_workspace(self, apply: bool = False) -> list[StandardizeResult]:
        """批量标准化工作空间所有项目

        Args:
            apply: False=仅检测预览, True=执行重命名

        Returns:
            所有项目的标准化结果列表
        """
        results: list[StandardizeResult] = []
        check_results = self.check_workspace()
        for cr in check_results:
            results.append(self.standardize_docs(cr.project_path, apply))
        return results

    # ── 内部方法 ──────────────────────────────────────────

    @staticmethod
    def _mkdir(path: str, dry_run: bool) -> None:
        if dry_run:
            return
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _write(path: str, content: str, dry_run: bool) -> None:
        if dry_run:
            return
        write_file(path, content)

    def _detect_project_type(self, project_path: str) -> str:
        """检测项目类型

        - standard: 标准 PLC 项目（有标准目录结构）
        - syslib_fb: SysLib 功能块项目（单 FB 目录，无标准子目录）
        """
        basename = os.path.basename(project_path)
        # SysLib FB 项目特征：以 FB_ 开头，且不在标准 PLC 项目目录下
        if basename.startswith("FB_") and "SysLib" in project_path:
            return "syslib_fb"
        return "standard"

    def _check_plc_json(self, project_path: str, result: CheckResult) -> None:
        """检查 .plc.json（LSP-907 §1）"""
        if result.project_type in SKIP_PLC_JSON_TYPES:
            result.add(".plc.json", "warn", "SysLib FB 项目通常无 .plc.json，如需要请手动创建")
            return

        plc_json_path = os.path.join(project_path, ".plc.json")
        if not os.path.isfile(plc_json_path):
            result.add(".plc.json", "fail", "缺少 .plc.json 配置文件（LSP-907 §1.1）")
            return

        try:
            with open(plc_json_path, encoding="utf-8") as f:
                cfg = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            result.add(".plc.json", "fail", f".plc.json 解析失败: {e}")
            return

        # 必填字段检查
        missing = [f for f in REQUIRED_PLC_JSON_FIELDS if f not in cfg]
        if missing:
            result.add(
                ".plc.json",
                "fail",
                f".plc.json 缺少必填字段: {', '.join(missing)}（LSP-907 §1.1）",
            )
        else:
            result.add(".plc.json", "pass", f"配置完整: name={cfg['name']}, version={cfg['version']}")

        # libraries 字段检查
        if "libraries" not in cfg or not cfg["libraries"]:
            result.add(".plc.json libraries", "warn", "未配置 libraries 字段，引用 SysLib 时需添加（LSP-907 §1.2）")
        else:
            # 检查 libraries 中配置的路径是否存在
            for lib_path in cfg["libraries"]:
                abs_lib = os.path.normpath(os.path.join(os.path.dirname(plc_json_path), lib_path))
                if os.path.isdir(abs_lib):
                    result.add(f".plc.json libraries[{lib_path}]", "pass", "库路径有效")
                else:
                    result.add(
                        f".plc.json libraries[{lib_path}]",
                        "warn",
                        f"库路径不存在: {abs_lib}",
                    )

    def _resolve_project_id(self, project_path: str) -> str:
        """从目录名解析项目编号

        支持多种命名模式：
        - DJ-2026-005_项目名 → DJ-2026-005
        - FB_1011_功能块名 → FB1011
        - SW-2026-005_项目名 → SW-2026-005
        """
        basename = os.path.basename(project_path)
        parts = basename.split("_", 1)
        if not parts:
            return basename
        first = parts[0]
        # FB 项目: FB_1011_Name → FB1011
        if first == "FB" and len(parts) > 1:
            second_parts = parts[1].split("_", 1)
            return f"FB{second_parts[0]}"
        return first

    def _check_pm_session(self, project_path: str, result: CheckResult) -> None:
        """检查 PM_SESSION"""
        project_id = self._resolve_project_id(project_path)

        pm_session = os.path.join(project_path, f"PM_SESSION_{project_id}.md")
        if os.path.isfile(pm_session):
            result.add("PM_SESSION", "pass", f"PM_SESSION_{project_id}.md 存在")
        else:
            # 尝试模糊匹配
            found = None
            try:
                for f in os.listdir(project_path):
                    if f.startswith("PM_SESSION_") and f.endswith(".md"):
                        found = f
                        break
            except OSError:
                pass
            if found:
                result.add("PM_SESSION", "warn", f"存在但命名不匹配: {found}，期望 PM_SESSION_{project_id}.md")
            else:
                result.add("PM_SESSION", "fail", f"缺少 PM_SESSION_{project_id}.md")

    def _check_prd_docs(self, project_path: str, result: CheckResult) -> None:
        """检查 PRD 文档完整性"""
        prd_path = os.path.join(project_path, "PRD")
        if not os.path.isdir(prd_path):
            result.add("PRD 目录", "fail", "缺少 PRD/ 目录")
            return

        result.add("PRD 目录", "pass", "PRD/ 目录存在")

        existing = set()
        try:
            existing = {f for f in os.listdir(prd_path) if f.endswith(".md")}
        except OSError:
            pass

        for doc in STD_PRDS:
            if doc in existing:
                result.add(f"PRD/{doc}", "pass", "存在")
            else:
                # 尝试模糊匹配
                prefix = doc.split("_")[0]
                matched = [f for f in existing if f.startswith(prefix)]
                if matched:
                    result.add(
                        f"PRD/{doc}",
                        "warn",
                        f"命名不匹配，实际文件: {', '.join(matched)}",
                    )
                else:
                    result.add(f"PRD/{doc}", "fail", f"缺少 {doc}")

    def _check_directory_structure(self, project_path: str, result: CheckResult) -> None:
        """检查目录结构是否符合 LSP-907 §3.1"""
        for d in STD_DIRS:
            full_path = os.path.join(project_path, d)
            if os.path.isdir(full_path):
                result.add(f"目录 {d}", "pass", "存在")
            else:
                result.add(f"目录 {d}", "fail", f"缺少目录 {d}（LSP-907 §3.1）")

    def _scan_and_check(
        self, path: str, results: list[CheckResult], depth: int, max_depth: int
    ) -> None:
        """递归扫描目录并检查项目

        项目识别规则（满足任一即识别为项目）：
        - 目录下存在 .plc.json（标准项目配置文件）
        - 目录下存在 PM_SESSION_*.md（项目管理会话文件）
        - 目录名以 FB_ 开头（SysLib 功能块项目）

        注意：不使用 .scl 文件和 PRD 目录作为识别规则，
        因为项目内的功能模块目录（如 OB1/pickplace/conveyor）也含 .scl 文件，
        会导致误识别。
        """
        if depth > max_depth:
            return

        try:
            entries = os.listdir(path)
        except OSError:
            return

        for entry in entries:
            entry_path = os.path.join(path, entry)
            if not os.path.isdir(entry_path):
                continue
            if entry.startswith("."):
                continue

            # 判断是否是项目目录
            try:
                sub_entries = os.listdir(entry_path)
            except OSError:
                sub_entries = []

            is_project = (
                # 规则1: 存在 .plc.json（标准项目配置文件）
                os.path.isfile(os.path.join(entry_path, ".plc.json"))
                # 规则2: 存在 PM_SESSION_*.md（项目管理会话文件）
                or any(f.startswith("PM_SESSION_") and f.endswith(".md") for f in sub_entries)
                # 规则3: 目录名以 FB_ 开头（SysLib 功能块项目）
                or entry.startswith("FB_")
            )

            if is_project:
                log.info("发现项目: %s", entry_path)
                results.append(self.check_project(entry_path))
                # 即使识别为项目，仍继续递归扫描子目录
                # （一个目录可能既是项目又是其他子项目的父目录，如 SysLib）
                if depth < max_depth:
                    self._scan_and_check(entry_path, results, depth + 1, max_depth)
            elif depth < max_depth:
                self._scan_and_check(entry_path, results, depth + 1, max_depth)

    # ── V9: 修复辅助方法 ──────────────────────────────────

    def _repair_plc_json(
        self, project_path: str, project_id: str, project_name: str,
        result: RepairResult, dry_run: bool
    ) -> None:
        """修复 .plc.json 缺失或字段不完整"""
        plc_json_path = os.path.join(project_path, ".plc.json")

        if not os.path.isfile(plc_json_path):
            # 缺失：生成模板（自动计算 libraries 相对路径）
            if not dry_run:
                libraries = self._compute_libraries(project_path)
                content = _plc_json_template(project_id, project_name)
                # 解析并替换 libraries
                cfg = json.loads(content)
                cfg["libraries"] = libraries
                write_file(plc_json_path, json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
            result.add(
                item=".plc.json",
                action="生成 .plc.json 模板",
                destructive=False,
                status="fixed" if not dry_run else "skipped",
                detail=f"创建 .plc.json（name={project_id}）" + (" [DRY-RUN]" if dry_run else ""),
            )
        else:
            # 字段不完整：补全缺失字段
            try:
                with open(plc_json_path, encoding="utf-8") as f:
                    cfg = json.load(f)
            except (json.JSONDecodeError, OSError):
                # 解析失败：覆盖为模板
                if not dry_run:
                    libraries = self._compute_libraries(project_path)
                    content = _plc_json_template(project_id, project_name)
                    cfg = json.loads(content)
                    cfg["libraries"] = libraries
                    write_file(plc_json_path, json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
                result.add(
                    item=".plc.json",
                    action="覆盖为模板（原文件解析失败）",
                    destructive=False,
                    status="fixed" if not dry_run else "skipped",
                    detail="原 .plc.json 解析失败，覆盖为模板" + (" [DRY-RUN]" if dry_run else ""),
                )
                return

            missing = [f for f in REQUIRED_PLC_JSON_FIELDS if f not in cfg]
            if missing:
                if not dry_run:
                    if "name" not in cfg:
                        cfg["name"] = project_id
                    if "description" not in cfg:
                        cfg["description"] = project_name
                    if "version" not in cfg:
                        cfg["version"] = "V1.0.0"
                    # 同时补全 libraries（若缺失或路径无效）
                    if "libraries" not in cfg or not cfg["libraries"]:
                        cfg["libraries"] = self._compute_libraries(project_path)
                    write_file(plc_json_path, json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
                result.add(
                    item=".plc.json",
                    action=f"补全缺失字段: {', '.join(missing)}",
                    destructive=False,
                    status="fixed" if not dry_run else "skipped",
                    detail=f"补全字段: {', '.join(missing)}" + (" [DRY-RUN]" if dry_run else ""),
                )

    def _compute_libraries(self, project_path: str) -> list[str]:
        """计算 .plc.json 中 libraries 的相对路径

        根据项目位置自动查找 01_SharedLibraries/SysLib 目录，
        计算相对于项目根目录的相对路径。

        Args:
            project_path: 项目根目录绝对路径

        Returns:
            libraries 相对路径列表（如 ["../../../01_SharedLibraries/SysLib"]）
        """
        # 从项目路径向上查找 01_SharedLibraries 目录
        current = os.path.dirname(project_path)
        for _ in range(5):  # 最多向上查找5层
            syslib_path = os.path.join(current, "01_SharedLibraries", "SysLib")
            if os.path.isdir(syslib_path):
                # 计算相对路径
                rel = os.path.relpath(syslib_path, project_path)
                # 统一为正斜杠（跨平台兼容）
                rel = rel.replace("\\", "/")
                return [rel]
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

        # 未找到 SysLib，返回默认路径（可能无效，但保持模板完整性）
        return ["../../../01_SharedLibraries/SysLib"]

    def _repair_pm_session(
        self, project_path: str, project_id: str, project_name: str,
        result: RepairResult, dry_run: bool
    ) -> None:
        """修复 PM_SESSION 缺失"""
        pm_session_path = os.path.join(project_path, f"PM_SESSION_{project_id}.md")

        if not dry_run:
            content = _pm_session_template(project_id, project_name, project_path)
            write_file(pm_session_path, content)
        result.add(
            item="PM_SESSION",
            action=f"生成 PM_SESSION_{project_id}.md 模板",
            destructive=False,
            status="fixed" if not dry_run else "skipped",
            detail=f"创建 PM_SESSION_{project_id}.md" + (" [DRY-RUN]" if dry_run else ""),
        )

    def _repair_prd_dir(
        self, project_path: str, project_id: str, project_name: str,
        result: RepairResult, dry_run: bool
    ) -> None:
        """修复 PRD 目录缺失（同时补全PRD四件套文档）"""
        prd_path = os.path.join(project_path, "PRD")
        if not dry_run:
            os.makedirs(prd_path, exist_ok=True)
        result.add(
            item="PRD 目录",
            action="创建 PRD/ 目录",
            destructive=False,
            status="fixed" if not dry_run else "skipped",
            detail="创建 PRD/ 目录" + (" [DRY-RUN]" if dry_run else ""),
        )

        # PRD 目录创建后，自动补全四件套文档
        template_map = {
            "需求分析文档_REQ.md": _req_template,
            "接口文档_INT.md": _int_template,
            "详细设计说明书_DSN.md": _dsn_template,
            "技术方案文档_TEC.md": _tec_template,
        }
        for doc_name, template_fn in template_map.items():
            doc_path = os.path.join(prd_path, doc_name)
            if not dry_run:
                content = template_fn(project_id, project_name)
                write_file(doc_path, content)
            result.add(
                item=f"PRD/{doc_name}",
                action=f"生成 {doc_name} 模板",
                destructive=False,
                status="fixed" if not dry_run else "skipped",
                detail=f"创建 {doc_name}" + (" [DRY-RUN]" if dry_run else ""),
            )

    def _repair_prd_doc(
        self, project_path: str, project_id: str, project_name: str,
        doc_name: str, result: RepairResult, dry_run: bool
    ) -> None:
        """修复 PRD 文档缺失"""
        prd_path = os.path.join(project_path, "PRD")
        doc_path = os.path.join(prd_path, doc_name)

        # 根据文档名选择模板函数
        template_map = {
            "需求分析文档_REQ.md": _req_template,
            "接口文档_INT.md": _int_template,
            "详细设计说明书_DSN.md": _dsn_template,
            "技术方案文档_TEC.md": _tec_template,
        }
        template_fn = template_map.get(doc_name)
        if not template_fn:
            result.add(
                item=f"PRD/{doc_name}",
                action="未知文档类型，跳过",
                destructive=False,
                status="skipped",
                detail=f"无模板映射: {doc_name}",
            )
            return

        if not dry_run:
            os.makedirs(prd_path, exist_ok=True)
            content = template_fn(project_id, project_name)
            write_file(doc_path, content)
        result.add(
            item=f"PRD/{doc_name}",
            action=f"生成 {doc_name} 模板",
            destructive=False,
            status="fixed" if not dry_run else "skipped",
            detail=f"创建 {doc_name}" + (" [DRY-RUN]" if dry_run else ""),
        )

    def _repair_std_dir(
        self, project_path: str, dir_name: str, result: RepairResult, dry_run: bool
    ) -> None:
        """修复 LSP-907 标准目录缺失"""
        dir_path = os.path.join(project_path, dir_name)
        if not dry_run:
            os.makedirs(dir_path, exist_ok=True)
        result.add(
            item=f"目录 {dir_name}",
            action=f"创建目录 {dir_name}",
            destructive=False,
            status="fixed" if not dry_run else "skipped",
            detail=f"创建目录 {dir_name}" + (" [DRY-RUN]" if dry_run else ""),
        )

    def _repair_rename(
        self, project_path: str, item: CheckItem,
        result: RepairResult, dry_run: bool
    ) -> None:
        """修复命名不匹配（破坏性操作：重命名）"""
        # 从检查项消息中提取实际文件名
        # 消息格式示例: "存在但命名不匹配: 接口文档_IFC-FB1012-V9.0.0.md，期望 接口文档_INT.md"
        message = item.message
        actual_file = ""
        expected_file = ""

        if "实际文件:" in message:
            # PRD 文档命名不匹配
            parts = message.split("实际文件:", 1)
            if len(parts) > 1:
                actual_part = parts[1].split("，")[0].strip()
                actual_file = actual_part.rstrip(",")

        if "期望" in message:
            parts = message.split("期望", 1)
            if len(parts) > 1:
                expected_file = parts[1].strip()

        if not actual_file or not expected_file:
            result.add(
                item=item.item,
                action="重命名文件（无法解析文件名）",
                destructive=True,
                status="failed",
                detail=f"无法从消息解析文件名: {message}",
            )
            return

        # 确定文件所在目录
        if item.item.startswith("PRD/"):
            base_dir = os.path.join(project_path, "PRD")
        else:
            base_dir = project_path

        old_path = os.path.join(base_dir, actual_file)
        new_path = os.path.join(base_dir, expected_file)

        if not os.path.isfile(old_path):
            result.add(
                item=item.item,
                action=f"重命名 {actual_file} → {expected_file}",
                destructive=True,
                status="failed",
                detail=f"原文件不存在: {old_path}",
            )
            return

        if dry_run:
            result.add(
                item=item.item,
                action=f"重命名 {actual_file} → {expected_file}",
                destructive=True,
                status="skipped",
                detail=f"[DRY-RUN] 将重命名并备份",
            )
            return

        try:
            # 备份原文件
            backup_path = old_path + ".bak"
            shutil.copy2(old_path, backup_path)

            # 执行重命名
            os.rename(old_path, new_path)

            # 更新关联引用
            if item.item.startswith("PRD/"):
                updates = self._update_references(base_dir, actual_file, expected_file)
                detail = f"重命名并备份: {actual_file} → {expected_file}"
                if updates:
                    detail += f"，更新引用: {len(updates)} 处"
            else:
                detail = f"重命名并备份: {actual_file} → {expected_file}"

            result.add(
                item=item.item,
                action=f"重命名 {actual_file} → {expected_file}",
                destructive=True,
                status="fixed",
                detail=detail,
            )
        except OSError as e:
            result.add(
                item=item.item,
                action=f"重命名 {actual_file} → {expected_file}",
                destructive=True,
                status="failed",
                detail=f"重命名失败: {e}",
            )

    def _update_references(
        self, prd_path: str, old_name: str, new_name: str
    ) -> list[str]:
        """更新 PRD 目录下其他文档中对旧文件名的引用

        Args:
            prd_path: PRD 目录路径
            old_name: 旧文件名
            new_name: 新文件名

        Returns:
            更新的文件列表
        """
        updates: list[str] = []
        try:
            files = [f for f in os.listdir(prd_path) if f.endswith(".md") and f != new_name]
        except OSError:
            return updates

        for filename in files:
            filepath = os.path.join(prd_path, filename)
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                if old_name in content:
                    new_content = content.replace(old_name, new_name)
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    updates.append(f"{filename}: {old_name} → {new_name}")
                    log.info("更新引用: %s - %s → %s", filename, old_name, new_name)
            except OSError as e:
                log.warning("更新引用失败: %s: %s", filename, e)

        return updates