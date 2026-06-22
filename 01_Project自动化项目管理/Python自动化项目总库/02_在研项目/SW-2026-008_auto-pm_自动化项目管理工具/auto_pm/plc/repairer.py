"""PLC 项目自动修复器（LSP-907 规范）

迁移自 SW-2026-005 的 PlcProjectService.repair_project/standardize_docs。
修复规则：
- 非破坏性操作（创建目录/文件/补全字段）：自动执行
- 破坏性操作（文件重命名）：需 rename_confirm=True
"""

from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime

from auto_pm.logging.logging import setup_logger
from auto_pm.plc.checker import PlcChecker
from auto_pm.plc.models import (
    NAMING_RULES,
    RenamePlan,
    RepairResult,
    StandardizeResult,
)

log = setup_logger(log_level="INFO", app_name="auto_pm")


class PlcRepairer:
    """PLC 项目自动修复器（LSP-907）"""

    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = os.path.abspath(workspace_root)
        self._checker = PlcChecker(workspace_root)

    # ── 单项目修复 ────────────────────────────────────────

    def repair_project(
        self,
        project_path: str,
        dry_run: bool = False,
        rename_confirm: bool = False,
    ) -> RepairResult:
        """自动修复项目结构问题

        Args:
            project_path: 项目根目录绝对路径
            dry_run: 仅预览不执行
            rename_confirm: 是否确认文件重命名（破坏性操作）

        Returns:
            RepairResult: 修复结果
        """
        log.info(
            "开始修复项目: %s (dry_run=%s, rename_confirm=%s)",
            project_path,
            dry_run,
            rename_confirm,
        )

        result = RepairResult(project_path=project_path)

        # 1. 修复前检查
        result.before_check = self._checker.check_project(project_path)

        project_id = self._checker.resolve_project_id(project_path)
        project_name = os.path.basename(project_path)

        # 2. 遍历检查项，对 FAIL 项执行修复
        for item in result.before_check.items:
            if item.status != "fail":
                continue

            if item.item == ".plc.json":
                self._repair_plc_json(
                    project_path, project_id, project_name, result, dry_run
                )
            elif item.item == "PM_SESSION":
                self._repair_pm_session(
                    project_path, project_id, project_name, result, dry_run
                )
            elif item.item == "PRD 目录":
                self._repair_prd_dir(
                    project_path, project_id, project_name, result, dry_run
                )
            elif item.item.startswith("PRD/"):
                doc_name = item.item.split("/", 1)[1]
                self._repair_prd_doc(
                    project_path, project_id, project_name, doc_name, result, dry_run
                )
            elif item.item.startswith("目录 "):
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
            for item in result.before_check.items:
                if item.status == "warn" and (
                    "命名不匹配" in item.message or "命名不规范" in item.message
                ):
                    result.add(
                        item=item.item,
                        action="重命名文件（需确认）",
                        destructive=True,
                        status="skipped",
                        detail=f"未确认重命名，跳过: {item.message}",
                    )

        # 4. 修复后重新检查
        if not dry_run:
            result.after_check = self._checker.check_project(project_path)
        else:
            result.after_check = result.before_check

        log.info(
            "修复完成: %s - fixed=%d skipped=%d failed=%d",
            os.path.basename(project_path),
            result.fixed_count,
            result.skipped_count,
            result.failed_count,
        )
        return result

    # ── 工作空间批量修复 ──────────────────────────────────

    def repair_workspace(
        self, dry_run: bool = False, rename_confirm: bool = False
    ) -> list[RepairResult]:
        """批量修复工作空间所有项目

        Args:
            dry_run: 仅预览不执行
            rename_confirm: 是否确认文件重命名

        Returns:
            所有需要修复的项目的修复结果列表（跳过已通过的项目）
        """
        results: list[RepairResult] = []
        check_results = self._checker.check_workspace()
        for cr in check_results:
            if cr.all_pass:
                continue
            results.append(
                self.repair_project(cr.project_path, dry_run, rename_confirm)
            )
        return results

    # ── 文档标准化 ────────────────────────────────────────

    def standardize_docs(
        self, project_path: str, apply: bool = False
    ) -> StandardizeResult:
        """检测并修正 PRD 文档命名

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

        try:
            existing_files = [f for f in os.listdir(prd_path) if f.endswith(".md")]
        except OSError as e:
            log.error("扫描 PRD 目录失败: %s", e)
            return result

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
                            backup_path = old_path + ".bak"
                            shutil.copy2(old_path, backup_path)
                            plan.backup_path = backup_path

                            os.rename(old_path, new_path)
                            plan.applied = True
                            result.applied_count += 1

                            updates = self._update_references(
                                prd_path, filename, std_name
                            )
                            result.reference_updates.extend(updates)

                            log.info("重命名: %s → %s", filename, std_name)
                        except OSError as e:
                            log.error("重命名失败: %s → %s: %s", filename, std_name, e)
                            result.skipped_count += 1
                    else:
                        result.skipped_count += 1

                    result.plans.append(plan)
                    break

        log.info(
            "标准化完成: %s - applied=%d skipped=%d",
            os.path.basename(project_path),
            result.applied_count,
            result.skipped_count,
        )
        return result

    def standardize_workspace(self, apply: bool = False) -> list[StandardizeResult]:
        """批量标准化工作空间所有项目"""
        results: list[StandardizeResult] = []
        check_results = self._checker.check_workspace()
        for cr in check_results:
            results.append(self.standardize_docs(cr.project_path, apply))
        return results

    # ── 内部修复方法 ──────────────────────────────────────

    def _repair_plc_json(
        self,
        project_path: str,
        project_id: str,
        project_name: str,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """修复 .plc.json（创建缺失文件或补全字段）"""
        plc_json_path = os.path.join(project_path, ".plc.json")

        if not os.path.isfile(plc_json_path):
            # 创建最小 .plc.json
            content = self._minimal_plc_json(project_id, project_name, plc_json_path)
            if not dry_run:
                with open(plc_json_path, "w", encoding="utf-8") as f:
                    f.write(content)
            result.add(
                item=".plc.json",
                action="创建 .plc.json",
                destructive=False,
                status="fixed",
                detail=f"已创建最小 .plc.json: name={project_id}",
            )
        else:
            # 补全缺失字段
            try:
                with open(plc_json_path, encoding="utf-8") as f:
                    cfg = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                result.add(
                    item=".plc.json",
                    action="修复 .plc.json 解析错误",
                    destructive=False,
                    status="failed",
                    detail=f"解析失败，需手动修复: {e}",
                )
                return

            changed = False
            if "name" not in cfg:
                cfg["name"] = project_id
                changed = True
            if "description" not in cfg:
                cfg["description"] = project_name
                changed = True
            if "version" not in cfg:
                cfg["version"] = "V1.0.0"
                changed = True

            if changed:
                if not dry_run:
                    with open(plc_json_path, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=2, ensure_ascii=False)
                result.add(
                    item=".plc.json",
                    action="补全 .plc.json 必填字段",
                    destructive=False,
                    status="fixed",
                    detail="已补全缺失的必填字段",
                )
            else:
                result.add(
                    item=".plc.json",
                    action="无需修复",
                    destructive=False,
                    status="skipped",
                    detail="字段完整，无需补全",
                )

    def _repair_pm_session(
        self,
        project_path: str,
        project_id: str,
        project_name: str,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """修复 PM_SESSION（创建缺失文件）"""
        pm_session_path = os.path.join(project_path, f"PM_SESSION_{project_id}.md")
        content = self._minimal_pm_session(project_id, project_name, project_path)

        if not dry_run:
            with open(pm_session_path, "w", encoding="utf-8") as f:
                f.write(content)
        result.add(
            item="PM_SESSION",
            action=f"创建 PM_SESSION_{project_id}.md",
            destructive=False,
            status="fixed",
            detail="已创建最小 PM_SESSION 骨架",
        )

    def _repair_prd_dir(
        self,
        project_path: str,
        project_id: str,
        project_name: str,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """修复 PRD 目录（创建缺失目录）"""
        prd_path = os.path.join(project_path, "PRD")
        if not dry_run:
            os.makedirs(prd_path, exist_ok=True)
        result.add(
            item="PRD 目录",
            action="创建 PRD/ 目录",
            destructive=False,
            status="fixed",
            detail="已创建 PRD/ 目录",
        )

    def _repair_prd_doc(
        self,
        project_path: str,
        project_id: str,
        project_name: str,
        doc_name: str,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """修复 PRD 文档（创建缺失文档）"""
        doc_path = os.path.join(project_path, "PRD", doc_name)
        content = self._minimal_prd_doc(doc_name, project_id, project_name)

        if not dry_run:
            os.makedirs(os.path.dirname(doc_path), exist_ok=True)
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(content)
        result.add(
            item=f"PRD/{doc_name}",
            action=f"创建 {doc_name}",
            destructive=False,
            status="fixed",
            detail=f"已创建最小 {doc_name} 骨架",
        )

    def _repair_std_dir(
        self,
        project_path: str,
        dir_name: str,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """修复标准目录（创建缺失目录）"""
        dir_path = os.path.join(project_path, dir_name)
        if not dry_run:
            os.makedirs(dir_path, exist_ok=True)
        result.add(
            item=f"目录 {dir_name}",
            action=f"创建目录 {dir_name}",
            destructive=False,
            status="fixed",
            detail=f"已创建目录 {dir_name}",
        )

    def _repair_rename(
        self,
        project_path: str,
        item: object,
        result: RepairResult,
        dry_run: bool,
    ) -> None:
        """执行文件重命名（破坏性操作）"""
        # 从检查项消息中解析实际文件名
        message = item.message  # type: ignore[attr-defined]
        match = re.search(r"实际文件: (.+)", message)
        if not match:
            result.add(
                item=item.item,  # type: ignore[attr-defined]
                action="重命名文件",
                destructive=True,
                status="failed",
                detail=f"无法解析实际文件名: {message}",
            )
            return

        actual_filename = match.group(1).strip()
        prd_path = os.path.join(project_path, "PRD")
        old_path = os.path.join(prd_path, actual_filename)

        # 推断标准名
        std_name = None
        for sn, rule in NAMING_RULES.items():
            if any(re.search(p, actual_filename) for p in rule["patterns"]):
                std_name = sn
                break

        if std_name is None:
            result.add(
                item=item.item,  # type: ignore[attr-defined]
                action="重命名文件",
                destructive=True,
                status="failed",
                detail=f"无法匹配标准命名: {actual_filename}",
            )
            return

        new_path = os.path.join(prd_path, std_name)

        if not dry_run:
            try:
                backup_path = old_path + ".bak"
                shutil.copy2(old_path, backup_path)
                os.rename(old_path, new_path)
                result.add(
                    item=item.item,  # type: ignore[attr-defined]
                    action=f"重命名 {actual_filename} → {std_name}",
                    destructive=True,
                    status="fixed",
                    detail=f"已重命名（备份: {os.path.basename(backup_path)}）",
                )
            except OSError as e:
                result.add(
                    item=item.item,  # type: ignore[attr-defined]
                    action="重命名文件",
                    destructive=True,
                    status="failed",
                    detail=f"重命名失败: {e}",
                )
        else:
            result.add(
                item=item.item,  # type: ignore[attr-defined]
                action=f"[DRY-RUN] 重命名 {actual_filename} → {std_name}",
                destructive=True,
                status="skipped",
                detail="dry_run 模式，未执行",
            )

    @staticmethod
    def _update_references(
        prd_path: str, old_name: str, new_name: str
    ) -> list[str]:
        """更新 PRD 目录内其他文档中对旧文件名的引用"""
        updates: list[str] = []
        try:
            for f in os.listdir(prd_path):
                if not f.endswith(".md") or f == new_name:
                    continue
                fpath = os.path.join(prd_path, f)
                try:
                    with open(fpath, encoding="utf-8") as fh:
                        content = fh.read()
                    if old_name in content:
                        new_content = content.replace(old_name, new_name)
                        with open(fpath, "w", encoding="utf-8") as fh:
                            fh.write(new_content)
                        updates.append(f"{f}: {old_name} → {new_name}")
                except OSError:
                    pass
        except OSError:
            pass
        return updates

    # ── 最小模板 ──────────────────────────────────────────

    @staticmethod
    def _minimal_plc_json(project_id: str, project_name: str, plc_json_path: str = "") -> str:
        """生成最小 .plc.json 内容

        Args:
            project_id: 项目ID
            project_name: 项目名称
            plc_json_path: .plc.json 文件所在路径，用于动态计算 libraries 相对路径。
                          空字符串时默认使用根级项目路径（../01_SharedLibraries/SysLib）。
        """
        # 动态计算 libraries 路径
        if not plc_json_path:
            # 默认：根级项目（.plc.json 在项目根目录）
            libraries_path = "../01_SharedLibraries/SysLib"
        else:
            # 根据 .plc.json 所在目录深度计算相对路径
            # 检测是否为嵌套项目（02_PLC程序/02_PLC程序/ 下）
            plc_json_dir = os.path.dirname(plc_json_path)
            # 统计路径中 02_PLC程序 出现的次数来判断嵌套深度
            depth = plc_json_dir.count("02_PLC程序")
            if depth >= 2:
                # 嵌套项目：02_PLC程序/02_PLC程序/.plc.json
                # 需要回退 3 级到项目根，再进入 01_SharedLibraries/SysLib
                libraries_path = "../../../01_SharedLibraries/SysLib"
            elif depth == 1:
                # 单层：02_PLC程序/.plc.json
                libraries_path = "../../01_SharedLibraries/SysLib"
            else:
                # 根级：.plc.json 在项目根
                libraries_path = "../01_SharedLibraries/SysLib"

        return json.dumps(
            {
                "name": project_id,
                "description": project_name,
                "version": "V1.0.0",
                "libraries": [libraries_path],
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n"

    @staticmethod
    def _minimal_pm_session(project_id: str, project_name: str, project_root: str) -> str:
        """生成最小 PM_SESSION 内容"""
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
- {today} | skill=auto-pm | mode=自动修复
  - goal: 补全缺失的 PM_SESSION
  - changed_files: PM_SESSION_{project_id}.md
  - impact: 项目管理会话文件就绪
  - risks: 无
"""

    @staticmethod
    def _minimal_prd_doc(doc_name: str, project_id: str, project_name: str) -> str:
        """生成最小 PRD 文档内容"""
        today = datetime.now().strftime("%Y-%m-%d")
        doc_type = doc_name.replace(".md", "")
        return f"""# {doc_type} - {project_id} {project_name}

> 项目编号: {project_id}
> 项目名称: {project_name}
> 创建日期: {today}

## 1. 概述
待补充

## 2. 变更记录
| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|---------|--------|
| {today} | V1.0.0 | 初始版本 | auto-pm |
"""
