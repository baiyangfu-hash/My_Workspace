"""PLC 项目结构检查器（LSP-907 规范）

迁移自 SW-2026-005 的 PlcProjectService.check_project/check_workspace。
检查项：.plc.json / PM_SESSION / PRD 文档 / 目录结构。
"""

from __future__ import annotations

import json
import os

from auto_pm.logging.logging import setup_logger
from auto_pm.plc.models import (
    REQUIRED_PLC_JSON_FIELDS,
    SKIP_PLC_JSON_TYPES,
    STD_DIRS,
    STD_PRDS,
    CheckResult,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")

# SysLib 关键文件清单（相对路径），用于 libraries 路径深度校验
_KEY_FILES = [
    "timer/FB_TON.scl",
    "counter/FB_CTD.scl",
    "counter/FB_CTU.scl",
    "edge/FB_R_TRIG.scl",
    "edge/FB_F_TRIG.scl",
]


class PlcChecker:
    """PLC 项目结构检查器（LSP-907）"""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)

    # ── 单项目检查 ────────────────────────────────────────

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

        # 4. 检查目录结构（仅标准项目）
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

    # ── 工作空间批量检查 ──────────────────────────────────

    def check_workspace(self, scan_depth: int = 4) -> list[CheckResult]:
        """扫描工作空间下所有项目并逐一检查

        Args:
            scan_depth: 扫描深度（默认4层）

        Returns:
            所有项目的检查结果列表
        """
        results: list[CheckResult] = []
        self._scan_and_check(self.workspace_root, results, depth=0, max_depth=scan_depth)
        return results

    # ── 内部方法 ──────────────────────────────────────────

    def _detect_project_type(self, project_path: str) -> str:
        """检测项目类型

        - standard: 标准 PLC 项目（有标准目录结构）
        - syslib_fb: SysLib 功能块项目（单 FB 目录，无标准子目录）
        """
        basename = os.path.basename(project_path)
        if basename.startswith("FB_") and "SysLib" in project_path:
            return "syslib_fb"
        return "standard"

    def resolve_project_id(self, project_path: str) -> str:
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

    def _check_plc_json(self, project_path: str, result: CheckResult) -> None:
        """检查 .plc.json（LSP-907 §1）"""
        if result.project_type in SKIP_PLC_JSON_TYPES:
            result.add(
                ".plc.json",
                "warn",
                "SysLib FB 项目通常无 .plc.json，如需要请手动创建",
            )
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
            result.add(
                ".plc.json",
                "pass",
                f"配置完整: name={cfg['name']}, version={cfg['version']}",
            )

        # libraries 字段检查
        if "libraries" not in cfg or not cfg["libraries"]:
            result.add(
                ".plc.json libraries",
                "warn",
                "未配置 libraries 字段，引用 SysLib 时需添加（LSP-907 §1.2）",
            )
        else:
            for lib_path in cfg["libraries"]:
                abs_lib = os.path.normpath(
                    os.path.join(os.path.dirname(plc_json_path), lib_path)
                )
                if not os.path.isdir(abs_lib):
                    result.add(
                        f".plc.json libraries[{lib_path}]",
                        "warn",
                        f"库路径不存在: {abs_lib}",
                    )
                    continue

                # 检查关键文件（深度校验）
                found_keys = [
                    key_file
                    for key_file in _KEY_FILES
                    if os.path.isfile(os.path.join(abs_lib, key_file))
                ]

                if found_keys:
                    result.add(
                        f".plc.json libraries[{lib_path}]",
                        "pass",
                        f"库路径有效，关键文件 {len(found_keys)}/{len(_KEY_FILES)}",
                    )
                else:
                    result.add(
                        f".plc.json libraries[{lib_path}]",
                        "warn",
                        f"库路径存在但关键文件缺失（期望: timer/counter/edge 等）",
                    )

    def _check_pm_session(self, project_path: str, result: CheckResult) -> None:
        """检查 PM_SESSION"""
        project_id = self.resolve_project_id(project_path)

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
                result.add(
                    "PM_SESSION",
                    "warn",
                    f"存在但命名不匹配: {found}，期望 PM_SESSION_{project_id}.md",
                )
            else:
                result.add("PM_SESSION", "fail", f"缺少 PM_SESSION_{project_id}.md")

    def _check_prd_docs(self, project_path: str, result: CheckResult) -> None:
        """检查 PRD 文档完整性"""
        prd_path = os.path.join(project_path, "PRD")
        if not os.path.isdir(prd_path):
            result.add("PRD 目录", "fail", "缺少 PRD/ 目录")
            return

        result.add("PRD 目录", "pass", "PRD/ 目录存在")

        existing: set[str] = set()
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
            if entry.startswith(".") or entry.startswith("__"):
                continue

            # 判断是否是项目目录
            if self._is_project_dir(entry_path):
                results.append(self.check_project(entry_path))
            else:
                # 非项目目录，继续递归
                self._scan_and_check(entry_path, results, depth + 1, max_depth)

    @staticmethod
    def _is_project_dir(project_path: str) -> bool:
        """判断目录是否为 PLC 项目

        识别规则（满足任一）：
        - 存在 .plc.json
        - 存在 PM_SESSION_*.md
        - 目录名以 FB_ 开头（SysLib FB 项目）
        """
        # .plc.json
        if os.path.isfile(os.path.join(project_path, ".plc.json")):
            return True

        # PM_SESSION_*.md
        try:
            for f in os.listdir(project_path):
                if f.startswith("PM_SESSION_") and f.endswith(".md"):
                    return True
        except OSError:
            pass

        # FB_ 开头（SysLib FB 项目）
        if os.path.basename(project_path).startswith("FB_"):
            return True

        return False
