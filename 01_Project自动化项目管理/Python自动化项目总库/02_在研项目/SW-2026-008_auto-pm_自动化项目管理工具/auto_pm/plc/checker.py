"""PLC-HMI 概念映射：SFB 库函数（PLC 检查器（验证 PLC 项目结构完整性））

像 PLC 的 SFB/SFC 系统函数，被 FB 功能块（application/*_facade.py）调用，
不直接暴露给 HMI 画面。

--- 原始注释 ---

PLC 项目结构检查器（LSP-907 907_项目配置规范_LSP）

迁移自 SW-2026-005 的 PlcProjectService.check_project/check_workspace。
检查项：.plc.json / PM_SESSION / PRD 文档 / 目录结构 / Spec Snapshot 规范漂移。
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import cast

from auto_pm.core.paths import find_prd_dir
from auto_pm.models.enums import ProjectType
from auto_pm.plc.models import (
    _LEGACY_PROJECT_INIT_PLC_PATH,
    NAMING_RULES,
    PM_DIR_CANDIDATES,
    REQUIRED_PLC_JSON_FIELDS,
    SKIP_PLC_JSON_TYPES,
    STD_DIRS,
    STD_PRDS,
    CheckResult,
)
from auto_pm.plc.spec_snapshot import (
    compare_versions,
    load_spec_registry,
    parse_spec_snapshot,
)

log = logging.getLogger(__name__)

# SysLib 关键文件清单（相对路径），用于 libraries 路径深度校验
_KEY_FILES = [
    "timer/FB_TON.scl",
    "counter/FB_CTD.scl",
    "counter/FB_CTU.scl",
    "edge/FB_R_TRIG.scl",
    "edge/FB_F_TRIG.scl",
]

# 真实历史 PLC 项目中常见的 PRD 文档落点。
# 仅在这些已知目录中做兼容识别，避免把任意散落文档误判为标准 PRD。
_LEGACY_PRD_DIRS = [
    os.path.join(*_LEGACY_PROJECT_INIT_PLC_PATH),
    "01_需求与设计",
    "01_需求与设计/13_软件方案",
    "02_PLC程序/PLC_ST/PRD",
    "02_PLC程序/程序文档",
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

        V0.4.1 Step 3: Python 项目（无 .plc.json + 有 pyproject.toml）直接返回
        not_applicable=True 的 CheckResult，不跑 5 项检查；规则与 _is_project_dir
        的 pyproject.toml 排除逻辑保持一致，避免 --all 模式与单项目模式行为分歧。
        """
        result = CheckResult(project_path=project_path)

        # V0.4.1 Step 3: Python 项目不适用 PLC 检查
        if not self._find_plc_json(project_path):
            if os.path.isfile(os.path.join(project_path, "pyproject.toml")):
                result.not_applicable = True
                result.not_applicable_reason = (
                    "Python 项目（无 .plc.json + 有 pyproject.toml），PLC 检查不适用"
                )
                log.info(
                    "Python 项目跳过 PLC 检查（not_applicable=True）: %s",
                    os.path.basename(project_path),
                )
                return result
            # V0.5.4: 位于 Python 项目管理区域且无 .plc.json 的遗留项目，PLC 检查不适用
            if self._is_in_python_area(project_path):
                result.not_applicable = True
                result.not_applicable_reason = (
                    "Python 区域遗留项目（无 .plc.json），PLC 检查不适用"
                )
                log.info(
                    "Python 区域遗留项目跳过 PLC 检查（not_applicable=True）: %s",
                    os.path.basename(project_path),
                )
                return result

        # 检测项目类型
        project_type = self._detect_project_type(project_path)
        result.project_type = cast(ProjectType, project_type)

        # 1. 检查 .plc.json
        self._check_plc_json(project_path, result)

        # 2. 检查 PM_SESSION
        self._check_pm_session(project_path, result)

        # 3. 检查 PRD 文档
        self._check_prd_docs(project_path, result)

        # 4. 检查目录结构（仅标准项目）
        if project_type == "standard":
            self._check_directory_structure(project_path, result)

        # 5. 检查 Spec Snapshot 规范漂移
        self._check_spec_snapshot(project_path, result)

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

        - standard: 标准 PLC 项目（有 00_项目管理 等标准目录结构）
        - shared-library: PLC 共享库（有 actuator/timer/counter 等模块目录）
        - test-suite: 测试套件项目（有 DB1/OB1/Test 但无标准目录）
        - syslib_fb: SysLib 功能块项目（单 FB 目录，无标准子目录）
        """
        basename = os.path.basename(project_path)
        if basename.startswith("FB_") and "SysLib" in project_path:
            return "syslib_fb"

        try:
            entries = set(os.listdir(project_path))
        except OSError:
            entries = set()

        # standard: 有项目管理目录（01_启动 或 00_项目管理，CHG-SCPT-2026-146 双向兼容）
        if any(c in entries for c in PM_DIR_CANDIDATES):
            return "standard"

        # shared-library: 有共享库特征目录
        shared_lib_markers = {
            "actuator",
            "timer",
            "counter",
            "edge",
            "convert",
            "log",
            "pulse",
            "communication",
            "types",
        }
        if shared_lib_markers & entries:
            return "shared-library"

        # test-suite: 有 DB1/OB1/Test 但无 00_项目管理
        test_suite_markers = {"DB1", "OB1", "Test"}
        if test_suite_markers & entries:
            return "test-suite"

        # 默认按 standard 检查（触发目录缺失告警）
        return "standard"

    @staticmethod
    def resolve_project_id(project_path: str) -> str:
        """从目录名解析项目编号

        支持多种命名模式：
        - DJ-2026-005_项目名 → DJ-2026-005
        - FB_1011_功能块名 → FB1011
        - SW-2026-005_项目名 → SW-2026-005

        V0.2.1-P2-4: 改为 staticmethod，供 CLI 层无实例调用。
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

    @staticmethod
    def _find_plc_json(project_path: str, max_depth: int = 3) -> str | None:
        """递归查找 .plc.json（与模板生成位置对齐）

        查找顺序：
        1. 项目根目录（标准位置）
        2. 子目录递归查找（适配 02_PLC程序/02_PLC程序/.plc.json 嵌套结构）

        Args:
            project_path: 项目根目录
            max_depth: 最大递归深度（默认3层）

        Returns:
            .plc.json 绝对路径，未找到返回 None
        """
        # 1. 根目录
        root_plc_json = os.path.join(project_path, ".plc.json")
        if os.path.isfile(root_plc_json):
            return root_plc_json

        # 2. 递归查找子目录
        def _search_dir(dir_path: str, depth: int) -> str | None:
            if depth > max_depth:
                return None
            try:
                entries = os.listdir(dir_path)
            except OSError:
                return None
            for entry in entries:
                entry_path = os.path.join(dir_path, entry)
                # 注意：不能跳过 .plc.json（它以 . 开头）
                if os.path.isfile(entry_path) and entry == ".plc.json":
                    return entry_path
                # 跳过隐藏目录和 Python 缓存目录（但保留 .plc.json 等配置文件）
                if entry.startswith(".") or entry.startswith("__"):
                    continue
                if os.path.isdir(entry_path):
                    found = _search_dir(entry_path, depth + 1)
                    if found:
                        return found
            return None

        return _search_dir(project_path, 1)

    def _check_plc_json(self, project_path: str, result: CheckResult) -> None:
        """检查 .plc.json（LSP-907 §1）"""
        if result.project_type in SKIP_PLC_JSON_TYPES:
            result.add(
                ".plc.json",
                "warn",
                "SysLib FB 项目通常无 .plc.json，如需要请手动创建",
            )
            return

        plc_json_path = self._find_plc_json(project_path)
        if not plc_json_path:
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
                abs_lib = os.path.normpath(os.path.join(os.path.dirname(plc_json_path), lib_path))
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
                        "库路径存在但关键文件缺失（期望: timer/counter/edge 等）",
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

    def _check_spec_snapshot(self, project_path: str, result: CheckResult) -> None:
        """检查 Spec Snapshot 规范漂移（V2.0.3）

        解析 PM_SESSION 中的 Spec Snapshot 表格，对比 spec_registry.json，
        根据漂移级别设置检查项状态：
        - major 漂移 → FAIL
        - minor/patch 漂移 → WARN
        - 无漂移 → PASS

        边界情况：
        - PM_SESSION 不存在 → 跳过（已在 PM_SESSION 检查中报告）
        - spec_registry.json 缺失 → WARN
        - Spec Snapshot 表格缺失 → WARN
        """
        # 查找 PM_SESSION 文件路径（复用现有查找逻辑）
        project_id = self.resolve_project_id(project_path)
        pm_session = os.path.join(project_path, f"PM_SESSION_{project_id}.md")
        if not os.path.isfile(pm_session):
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
                pm_session = os.path.join(project_path, found)
            else:
                # PM_SESSION 不存在，已在第 2 项检查中报告
                return

        # 加载 spec_registry.json
        registry = load_spec_registry(self.workspace_root)
        if registry is None:
            result.add(
                "Spec Snapshot",
                "warn",
                "未找到 spec_registry.json，跳过漂移检测",
            )
            return

        # 解析 Spec Snapshot 表格
        snapshot = parse_spec_snapshot(pm_session)
        if not snapshot:
            result.add(
                "Spec Snapshot",
                "warn",
                "PM_SESSION 缺少 Spec Snapshot 表格",
            )
            return

        # 对比版本
        drifts = compare_versions(snapshot, registry)
        if not drifts:
            result.add(
                "Spec Snapshot",
                "pass",
                "Spec Snapshot 与 spec_registry.json 一致",
            )
            return

        # 根据漂移级别设置状态
        level_names = {
            "major": "主版本漂移",
            "minor": "次版本漂移",
            "patch": "补丁漂移",
        }
        drift_msgs = [
            f"{d.spec_id}: {d.snapshot_version} → {d.registry_version} "
            f"({level_names[d.drift_level]})"
            for d in drifts
        ]
        has_major = any(d.drift_level == "major" for d in drifts)
        status = "fail" if has_major else "warn"
        result.add("Spec Snapshot", status, "; ".join(drift_msgs))

    def _check_prd_docs(self, project_path: str, result: CheckResult) -> None:
        """检查 PRD 文档完整性"""
        found = find_prd_dir(project_path)
        legacy_dirs = self._get_existing_legacy_prd_dirs(project_path)

        if found is None:
            if legacy_dirs:
                result.add(
                    "PRD 目录",
                    "warn",
                    "未使用 root PRD/ 或 00_程序方案/，检测到历史文档目录: "
                    + ", ".join(legacy_dirs),
                )
            else:
                result.add("PRD 目录", "fail", "缺少 PRD/（或 00_程序方案/）目录")
                return
        else:
            prd_path, prd_name = found
            result.add("PRD 目录", "pass", f"{prd_name}/ 目录存在")

        existing: set[str] = set()
        try:
            if found is not None:
                prd_path = found[0]
                existing = {f for f in os.listdir(prd_path) if f.endswith(".md")}
        except OSError:
            pass

        prd_display_name = found[1] if found else "PRD"
        for doc in STD_PRDS:
            if doc in existing:
                result.add(f"{prd_display_name}/{doc}", "pass", "存在")
            else:
                # 尝试模糊匹配
                prefix = doc.split("_")[0]
                matched = [f for f in existing if f.startswith(prefix)]
                if matched:
                    result.add(
                        f"{prd_display_name}/{doc}",
                        "warn",
                        f"命名不匹配，实际文件: {', '.join(matched)}",
                    )
                else:
                    legacy_matches = self._find_legacy_prd_docs(project_path, doc)
                    if legacy_matches:
                        result.add(
                            f"{prd_display_name}/{doc}",
                            "warn",
                            "历史路径存在: "
                            + ", ".join(legacy_matches)
                            + f"，建议后续收口到 {prd_display_name}/",
                        )
                    else:
                        result.add(
                            f"{prd_display_name}/{doc}", "fail", f"缺少 {doc}"
                        )

    @staticmethod
    def _get_existing_legacy_prd_dirs(project_path: str) -> list[str]:
        """返回存在的历史 PRD 目录（相对路径，使用 / 分隔）"""
        existing_dirs: list[str] = []
        for rel_dir in _LEGACY_PRD_DIRS:
            abs_dir = os.path.join(project_path, rel_dir)
            if os.path.isdir(abs_dir):
                existing_dirs.append(rel_dir.replace(os.sep, "/"))
        return existing_dirs

    @staticmethod
    def _find_legacy_prd_docs(project_path: str, doc_name: str) -> list[str]:
        """在受控历史目录中查找等价 PRD 文档"""
        rule = NAMING_RULES.get(doc_name, {})
        patterns = [re.compile(p) for p in rule.get("patterns", [])]
        prefix = doc_name.split("_")[0]
        matches: list[str] = []

        for rel_dir in _LEGACY_PRD_DIRS:
            abs_dir = os.path.join(project_path, rel_dir)
            if not os.path.isdir(abs_dir):
                continue

            try:
                md_files = sorted(f for f in os.listdir(abs_dir) if f.endswith(".md"))
            except OSError:
                continue

            for filename in md_files:
                if filename == doc_name:
                    matches.append(f"{rel_dir}/{filename}".replace(os.sep, "/"))
                    continue

                if filename.startswith(prefix) or any(
                    pattern.search(filename) for pattern in patterns
                ):
                    matches.append(f"{rel_dir}/{filename}".replace(os.sep, "/"))

        return matches

    def _check_directory_structure(self, project_path: str, result: CheckResult) -> None:
        """检查目录结构是否符合 LSP-907 §3.1

        CHG-SCPT-2026-146: 双向兼容 01_启动（新模板）和 00_项目管理（旧项目）
        """
        for d in STD_DIRS:
            full_path = os.path.join(project_path, d)
            if os.path.isdir(full_path):
                result.add(f"目录 {d}", "pass", "存在")
            # 项目管理目录：接受任一候选（01_启动 或 00_项目管理）
            elif d in PM_DIR_CANDIDATES and any(
                os.path.isdir(os.path.join(project_path, c))
                for c in PM_DIR_CANDIDATES
            ):
                # 找到实际存在的候选目录名用于报告
                actual = next(
                    c for c in PM_DIR_CANDIDATES
                    if os.path.isdir(os.path.join(project_path, c))
                )
                result.add(f"目录 {actual}", "pass", "存在（5大过程组兼容）")
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
        - 存在 .plc.json（仅根目录，不递归查找，避免将容器目录误判为项目）
        - 存在 PM_SESSION_*.md 且位于 PLC 区域
        - 目录名以 FB_ 开头（SysLib FB 项目）

        排除规则：
        - 存在 pyproject.toml 且无 .plc.json → Python 项目，跳过
        - 位于 Python 项目管理区域且无 .plc.json → 非 PLC 项目，跳过
        - 仅靠 PM_SESSION 识别且不在 PLC 区域 → 非 PLC 项目（如 SYS-2026-001 跨域治理项目），跳过
        """
        # .plc.json（仅根目录，不递归查找，防止将 0100_PLC自动化 等容器目录误判为项目）
        if os.path.isfile(os.path.join(project_path, ".plc.json")):
            return True

        # 排除 Python 项目（有 pyproject.toml 且无 .plc.json）
        if os.path.isfile(os.path.join(project_path, "pyproject.toml")):
            return False

        # 排除 Python 项目管理区域的项目（无 .plc.json 且位于 Python 项目目录下）
        if PlcChecker._is_in_python_area(project_path):
            return False

        # PM_SESSION_*.md（仅 PLC 区域内的项目，避免将 SYS-2026-001 等跨域项目误判为 PLC 项目）
        has_pm_session = False
        try:
            for f in os.listdir(project_path):
                if f.startswith("PM_SESSION_") and f.endswith(".md"):
                    has_pm_session = True
                    break
        except OSError:
            pass

        if has_pm_session and PlcChecker._is_in_plc_area(project_path):
            return True

        # FB_ 开头（SysLib FB 项目）
        if os.path.basename(project_path).startswith("FB_"):
            return True

        return False

    @staticmethod
    def _is_in_python_area(project_path: str) -> bool:
        """判断项目路径是否位于 Python 项目管理区域

        用于在 PLC 扫描中排除非 PLC 项目。
        规则：路径中包含 01_Project自动化项目管理/Python自动化项目总库 即视为 Python 区域。
        """
        norm_path = project_path.replace("/", os.sep)
        python_marker = "01_Project自动化项目管理" + os.sep + "Python自动化项目总库" + os.sep
        return python_marker in norm_path

    @staticmethod
    def _is_in_plc_area(project_path: str) -> bool:
        """判断项目路径是否位于 PLC 自动化区域

        规则：路径中包含 0100_PLC自动化 即视为 PLC 区域。
        """
        norm_path = project_path.replace("/", os.sep)
        plc_marker = os.sep + "0100_PLC自动化" + os.sep
        return plc_marker in norm_path
