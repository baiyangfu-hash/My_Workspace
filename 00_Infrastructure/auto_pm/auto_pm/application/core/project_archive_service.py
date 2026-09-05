"""项目全生命周期归档与恢复引擎 (ProjectArchiveService)

消除物理 hard delete 风险，提供：
1. 领域就近路由 (resolve_archive_path)
2. 三道硬门禁 (check_archive_gates): 未闭环变更单拦截、Git脏状态拦截、系统级母体保护与管理资产合规
3. 归档台账自动化: 自动初始化/更新 00_历史项目归档台账.md，流水编号 ARC-YYYYMMDD-XXX
4. 逆向恢复引擎 (restore_project): 恢复至在研目录、冲突防护、台账与 DB 缓存同步
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from auto_pm.db.connection import DatabaseManager
    from auto_pm.models import ProjectInfo

log = logging.getLogger(__name__)

# 受保护的项目编号（核心母体与系统级资产严禁归档）
PROTECTED_PROJECT_IDS: frozenset[str] = frozenset({"SW-2026-008", "SYS-2026-001"})

LEDGER_FILENAME = "00_历史项目归档台账.md"
LEDGER_HEADER = "| 序号 | 归档编号 | 项目编号 | 项目名称 | 技术栈 | 原路径 | 归档路径 | 归档日期 | 归档人 | 归档原因 | 状态 |"
LEDGER_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"


class ProjectArchiveError(Exception):
    """项目归档/恢复通用异常基类"""


class OpenChangesBlockingError(ProjectArchiveError):
    """未闭环变更单阻断异常"""


class DirtyWorkspaceBlockingError(ProjectArchiveError):
    """Git 工作区脏状态阻断异常"""


class ProtectionViolationError(ProjectArchiveError):
    """受保护项目归档阻断异常"""


class ProjectArchiveService:
    """项目归档与恢复服务"""

    def __init__(self, workspace_root: str, db: DatabaseManager | None = None) -> None:
        self.workspace_root = os.path.abspath(workspace_root)
        self.db = db

    # ── 机制一：领域就近路由 ─────────────────────────────

    def resolve_archive_path(self, project_path: str) -> str:
        """根据项目源路径解析归档目标路径

        路由规则：
        1. 源路径包含 0100_PLC自动化 -> <ws>/0100_PLC自动化/_archive/<project_dirname>
        2. 源路径包含 01_Project自动化项目管理/Python自动化项目总库/02_在研项目 ->
           <ws>/01_Project自动化项目管理/Python自动化项目总库/03_归档/<project_dirname>
        3. 其他路径 -> 所在上级目录下的 _archive/<project_dirname>
        """
        abs_path = os.path.abspath(project_path)
        project_dirname = os.path.basename(abs_path)
        rel_path = os.path.relpath(abs_path, self.workspace_root).replace("\\", "/")

        if "0100_PLC自动化" in rel_path:
            archive_dir = os.path.join(self.workspace_root, "0100_PLC自动化", "_archive")
        elif "01_Project自动化项目管理/Python自动化项目总库/02_在研项目" in rel_path:
            archive_dir = os.path.join(
                self.workspace_root,
                "01_Project自动化项目管理",
                "Python自动化项目总库",
                "03_归档",
            )
        else:
            parent_dir = os.path.dirname(abs_path)
            archive_dir = os.path.join(parent_dir, "_archive")

        return os.path.join(archive_dir, project_dirname)

    def resolve_restore_path(self, current_archive_path: str, orig_rel_path: str | None = None) -> str:
        """根据当前归档路径逆向推导恢复目标路径

        恢复路由：
        1. 若当前路径在 0100_PLC自动化/_archive -> 恢复至 <ws>/0100_PLC自动化/<dirname>
        2. 若在 Python自动化项目总库/03_归档 -> 恢复至 Python自动化项目总库/02_在研项目/<dirname>
        3. 若位于任意 .../_archive/<dirname> -> 恢复至 .../<dirname> (上级目录)
        4. 备选：若有记录 orig_rel_path 且位于 workspace 下，优先尝试还原原相对路径
        """
        abs_archive = os.path.abspath(current_archive_path)
        project_dirname = os.path.basename(abs_archive)
        rel_archive = os.path.relpath(abs_archive, self.workspace_root).replace("\\", "/")

        if "0100_PLC自动化/_archive" in rel_archive:
            return os.path.join(self.workspace_root, "0100_PLC自动化", project_dirname)

        if "01_Project自动化项目管理/Python自动化项目总库/03_归档" in rel_archive:
            return os.path.join(
                self.workspace_root,
                "01_Project自动化项目管理",
                "Python自动化项目总库",
                "02_在研项目",
                project_dirname,
            )

        if os.path.basename(os.path.dirname(abs_archive)) == "_archive":
            parent_dir = os.path.dirname(os.path.dirname(abs_archive))
            return os.path.join(parent_dir, project_dirname)

        if orig_rel_path:
            candidate = os.path.abspath(os.path.join(self.workspace_root, orig_rel_path))
            return candidate

        parent_dir = os.path.dirname(os.path.dirname(abs_archive))
        return os.path.join(parent_dir, project_dirname)

    # ── 机制二：三道硬门禁 ─────────────────────────────

    def check_archive_gates(self, project_id: str, project_path: str, force: bool = False) -> None:
        """执行归档前的三道硬门禁检查

        Gate 1：未闭环变更单拦截（状态非 completed/closed/archived 阻断）
        Gate 2：Git 工作区脏状态拦截（未提交/未追踪文件阻断，force=True 可绕过）
        Gate 3：核心母体保护与管理资产合规（SW-2026-008/SYS-2026-001 严禁归档，必须存在 PM_SESSION_*.md）
        """
        # Gate 3 先行：核心母体保护
        if project_id in PROTECTED_PROJECT_IDS:
            raise ProtectionViolationError(
                f"核心母体/系统级受保护项目严禁归档: {project_id}"
            )

        if not os.path.isdir(project_path):
            raise FileNotFoundError(f"项目目录不存在: {project_path}")

        # Gate 3 后半：管理资产合规（校验根目录下必须存在 PM_SESSION_*.md）
        pm_files = [
            f for f in os.listdir(project_path)
            if f.startswith("PM_SESSION_") and f.endswith(".md")
        ]
        if not pm_files:
            raise ProjectArchiveError(
                f"项目缺少 PM_SESSION_*.md 管理资产文件，不符合归档合规要求: {project_path}"
            )

        # Gate 1：未闭环变更单拦截
        from auto_pm.change.change_service import ChangeService
        change_service = ChangeService(self.workspace_root, db=self.db)
        try:
            changes = change_service.list_change_requests(project_id)
            open_changes = [
                c for c in changes
                if c.status not in ("completed", "closed", "archived")
            ]
            if open_changes:
                open_ids = [c.change_number for c in open_changes]
                raise OpenChangesBlockingError(
                    f"项目 {project_id} 存在未闭环变更单: {open_ids}，禁止归档"
                )
        except OpenChangesBlockingError:
            raise
        except Exception as e:
            log.warning("变更单门禁检查异常: %s", e)

        # Gate 2：Git 工作区脏状态拦截
        if not force:
            try:
                proc = subprocess.run(
                    ["git", "status", "--porcelain", "."],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                if proc.returncode == 0:
                    dirty_output = proc.stdout.strip()
                    if dirty_output:
                        raise DirtyWorkspaceBlockingError(
                            f"项目工作区存在未提交变更或未追踪文件，禁止归档（可使用 force=True 强制归档）:\n{dirty_output}"
                        )
            except DirtyWorkspaceBlockingError:
                raise
            except FileNotFoundError:
                # 环境未安装 git 命令时放行
                pass
            except Exception as e:
                log.warning("Git 脏状态检查异常: %s", e)

    # ── 机制三：归档台账自动化 ──────────────────────────

    def _ensure_ledger(self, archive_dir: str) -> str:
        """确保归档目录存在 00_历史项目归档台账.md，不存在则初始化"""
        os.makedirs(archive_dir, exist_ok=True)
        ledger_path = os.path.join(archive_dir, LEDGER_FILENAME)
        if not os.path.isfile(ledger_path):
            initial_content = (
                "# 历史项目归档台账\n\n"
                "> 本目录记录已归档历史项目的流水与恢复追踪台账。\n\n"
                f"{LEDGER_HEADER}\n"
                f"{LEDGER_SEPARATOR}\n"
            )
            with open(ledger_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(initial_content)
        return ledger_path

    def _generate_archive_code(self, ledger_path: str) -> str:
        """根据台账生成流水编号 ARC-YYYYMMDD-XXX"""
        today_str = datetime.now().strftime("%Y%m%d")
        prefix = f"ARC-{today_str}-"
        max_seq = 0

        if os.path.isfile(ledger_path):
            try:
                with open(ledger_path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        m = re.search(r"ARC-" + today_str + r"-(\d{3})", line)
                        if m:
                            seq = int(m.group(1))
                            if seq > max_seq:
                                max_seq = seq
            except OSError:
                pass

        return f"{prefix}{max_seq + 1:03d}"

    def _count_ledger_entries(self, ledger_path: str) -> int:
        """统计台账中已有的数据行数量"""
        count = 0
        if os.path.isfile(ledger_path):
            try:
                with open(ledger_path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("|") and not line.startswith("|-") and "归档编号" not in line:
                            parts = [p.strip() for p in line.split("|")[1:-1]]
                            if parts and parts[0].isdigit():
                                count += 1
            except OSError:
                pass
        return count

    def _append_ledger_entry(
        self,
        ledger_path: str,
        archive_code: str,
        project_id: str,
        project_name: str,
        stack: str,
        orig_path: str,
        archive_path: str,
        operator: str,
        reason: str,
    ) -> None:
        """在台账中追加归档记录"""
        seq = self._count_ledger_entries(ledger_path) + 1
        today = datetime.now().strftime("%Y-%m-%d")
        rel_orig = os.path.relpath(orig_path, self.workspace_root).replace("\\", "/")
        rel_dest = os.path.relpath(archive_path, self.workspace_root).replace("\\", "/")

        row = (
            f"| {seq} | {archive_code} | {project_id} | {project_name} | {stack} | "
            f"{rel_orig} | {rel_dest} | {today} | {operator} | {reason} | 已归档 |\n"
        )
        with open(ledger_path, "a", encoding="utf-8", errors="replace") as f:
            f.write(row)

    def _update_ledger_entry_status(
        self,
        ledger_path: str,
        project_id: str,
        new_status: str = "已恢复",
    ) -> bool:
        """更新台账中指定项目的状态为已恢复"""
        if not os.path.isfile(ledger_path):
            return False

        with open(ledger_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        updated = False
        new_lines: list[str] = []
        for line in lines:
            if line.strip().startswith("|") and f"| {project_id} |" in line:
                parts = [p.strip() for p in line.strip().split("|")[1:-1]]
                if len(parts) >= 11:
                    parts[10] = new_status
                    line = "| " + " | ".join(parts) + " |\n"
                    updated = True
            new_lines.append(line)

        if updated:
            with open(ledger_path, "w", encoding="utf-8", errors="replace") as f:
                f.writelines(new_lines)

        return updated

    def _find_ledger_entry(self, archive_dir: str, project_id: str) -> dict[str, str] | None:
        """在台账中按 project_id 查找最新的一条归档记录"""
        ledger_path = os.path.join(archive_dir, LEDGER_FILENAME)
        if not os.path.isfile(ledger_path):
            return None

        found_entry: dict[str, str] | None = None
        try:
            with open(ledger_path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.strip().startswith("|") and f"| {project_id} |" in line:
                        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
                        if len(parts) >= 11:
                            found_entry = {
                                "seq": parts[0],
                                "archive_code": parts[1],
                                "project_id": parts[2],
                                "project_name": parts[3],
                                "stack": parts[4],
                                "orig_path": parts[5],
                                "archive_path": parts[6],
                                "archive_date": parts[7],
                                "operator": parts[8],
                                "reason": parts[9],
                                "status": parts[10],
                            }
        except OSError:
            pass

        return found_entry

    def _update_project_phase(self, project_path: str, new_phase: str) -> None:
        """更新项目 PM_SESSION 与 .copier-answers.yml 中的 phase 字段"""
        if not os.path.isdir(project_path):
            return

        # 1. 更新 PM_SESSION_*.md
        for fname in os.listdir(project_path):
            if fname.startswith("PM_SESSION_") and fname.endswith(".md"):
                file_path = os.path.join(project_path, fname)
                try:
                    with open(file_path, encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    # 若有 frontmatter phase，替换之
                    if re.search(r"^phase:\s*.*$", content, re.MULTILINE):
                        content = re.sub(
                            r"^phase:\s*.*$",
                            f"phase: {new_phase}",
                            content,
                            flags=re.MULTILINE,
                        )
                    elif re.search(r"^\|\s*阶段\s*\|\s*.*?\s*\|$", content, re.MULTILINE):
                        content = re.sub(
                            r"^\|\s*阶段\s*\|\s*.*?\s*\|$",
                            f"| 阶段 | {new_phase} |",
                            content,
                            flags=re.MULTILINE,
                        )
                    else:
                        # 既无 frontmatter 也无表格，在开头或头部追加 frontmatter
                        if content.startswith("---"):
                            second_dash = content.find("---", 3)
                            if second_dash != -1:
                                content = content[:second_dash] + f"phase: {new_phase}\n" + content[second_dash:]
                        else:
                            content = f"---\nphase: {new_phase}\n---\n\n" + content

                    with open(file_path, "w", encoding="utf-8", errors="replace") as f:
                        f.write(content)
                except OSError as e:
                    log.warning("更新 PM_SESSION phase 失败: %s", e)

        # 2. 更新 .copier-answers.yml（若存在）
        copier_file = os.path.join(project_path, ".copier-answers.yml")
        if os.path.isfile(copier_file):
            try:
                import yaml
                with open(copier_file, encoding="utf-8", errors="replace") as f:
                    data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    data["phase"] = new_phase
                    with open(copier_file, "w", encoding="utf-8", errors="replace") as f:
                        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
            except Exception as e:
                log.warning("更新 .copier-answers.yml phase 失败: %s", e)

    # ── 归档主入口 ─────────────────────────────────────

    def archive_project(
        self,
        project_id: str,
        reason: str = "",
        operator: str = "fubai",
        force: bool = False,
    ) -> dict[str, Any]:
        """将项目归档至对应的领域归档目录

        Args:
            project_id: 项目编号（如 SW-2026-001）
            reason: 归档原因
            operator: 归档操作人
            force: 强制归档（跳过 Git 脏状态拦截）

        Returns:
            归档结果字典，包含 archive_code、archive_path 等信息
        """
        # 1. 查找待归档项目
        from auto_pm.core.project_service import ProjectService
        svc = ProjectService(self.workspace_root, db=self.db)
        proj = svc.get_project(project_id)
        if proj is None:
            raise FileNotFoundError(f"项目不存在: {project_id}")

        project_path = os.path.abspath(proj.path)

        # 2. 三道硬门禁检查
        self.check_archive_gates(project_id, project_path, force=force)

        # 3. 解析领域就近路由
        archive_path = self.resolve_archive_path(project_path)
        archive_dir = os.path.dirname(archive_path)

        if os.path.exists(archive_path):
            raise FileExistsError(f"归档目标路径已存在同名项目: {archive_path}")

        # 4. 准备归档台账与生成归档编号
        ledger_path = self._ensure_ledger(archive_dir)
        archive_code = self._generate_archive_code(ledger_path)

        # 5. 物理迁移目录
        os.makedirs(archive_dir, exist_ok=True)
        shutil.move(project_path, archive_path)

        # 6. 更新项目元数据中的 phase 为 archived
        self._update_project_phase(archive_path, "archived")

        # 7. 追加台账记录
        self._append_ledger_entry(
            ledger_path=ledger_path,
            archive_code=archive_code,
            project_id=project_id,
            project_name=proj.name,
            stack=proj.stack,
            orig_path=project_path,
            archive_path=archive_path,
            operator=operator,
            reason=reason or "项目生命周期完结归档",
        )

        # 8. 同步 DB 缓存
        if self.db is not None:
            try:
                svc.sync_to_cache(force_full=True)
            except Exception as e:
                log.warning("归档后 DB 缓存同步失败: %s", e)

        log.info("项目已归档: %s -> %s (编号: %s)", project_id, archive_path, archive_code)
        return {
            "success": True,
            "project_id": project_id,
            "archive_code": archive_code,
            "archive_path": archive_path,
            "orig_path": project_path,
        }

    # ── 机制四：逆向恢复引擎 ───────────────────────────

    def restore_project(
        self,
        project_id: str,
        dest_dir: str | None = None,
        operator: str = "fubai",
    ) -> dict[str, Any]:
        """从归档目录将项目恢复至活跃在研目录

        Args:
            project_id: 项目编号
            dest_dir: 可选，指定恢复到的在研父目录；若未提供则自动执行逆向路由推导
            operator: 恢复操作人

        Returns:
            恢复结果字典，包含 restored_path 等信息
        """
        # 1. 在归档目录中定位该项目
        archived_projects = self.list_archived_projects()
        target_proj = next((p for p in archived_projects if p.project_id == project_id), None)

        if target_proj is None:
            raise FileNotFoundError(f"归档项目中未找到: {project_id}")

        current_archive_path = os.path.abspath(target_proj.path)
        archive_dir = os.path.dirname(current_archive_path)

        # 2. 获取台账中的原始记录
        ledger_entry = self._find_ledger_entry(archive_dir, project_id)
        orig_rel_path = ledger_entry.get("orig_path") if ledger_entry else None

        # 3. 确定目标恢复路径
        project_dirname = os.path.basename(current_archive_path)
        if dest_dir:
            restored_path = os.path.abspath(os.path.join(dest_dir, project_dirname))
        else:
            restored_path = self.resolve_restore_path(current_archive_path, orig_rel_path)

        # 4. 冲突防护：目标在研路径若已存在同名目录则阻断
        if os.path.exists(restored_path):
            raise FileExistsError(f"目标在研路径已存在同名目录，拒绝恢复覆盖: {restored_path}")

        # 5. 物理回迁
        os.makedirs(os.path.dirname(restored_path), exist_ok=True)
        shutil.move(current_archive_path, restored_path)

        # 6. 更新 PM_SESSION 和 .copier-answers.yml 中的 phase 为 developing
        self._update_project_phase(restored_path, "developing")

        # 7. 更新台账状态为 已恢复
        ledger_path = os.path.join(archive_dir, LEDGER_FILENAME)
        self._update_ledger_entry_status(ledger_path, project_id, new_status="已恢复")

        # 8. 同步 DB 缓存
        if self.db is not None:
            try:
                from auto_pm.core.project_service import ProjectService
                svc = ProjectService(self.workspace_root, db=self.db)
                svc.sync_to_cache(force_full=True)
            except Exception as e:
                log.warning("恢复后 DB 缓存同步失败: %s", e)

        log.info("项目已恢复: %s -> %s (操作人: %s)", project_id, restored_path, operator)
        return {
            "success": True,
            "project_id": project_id,
            "restored_path": restored_path,
            "archive_path": current_archive_path,
        }

    # ── 归档项目列表 ───────────────────────────────────

    def list_archived_projects(self) -> list[ProjectInfo]:
        """扫描所有归档项目并返回"""
        from auto_pm.core.project_scanner import ProjectScanner
        scanner = ProjectScanner(self.workspace_root)
        return cast(list["ProjectInfo"], scanner.scan_archived())

