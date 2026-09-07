"""PLC-HMI 概念映射：SFB 库函数（规范索引（生成规范文档索引））

像 PLC 的 SFB/SFC 系统函数，被 FB 功能块（application/*_facade.py）调用，
不直接暴露给 HMI 画面。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from auto_pm.spec.core.config import (
    AUTO_GENERATED_HEADER,
    DEFAULT_OUTPUT_PATHS,
    DOMAIN_CONFIG,
    WorkspaceConfig,
)
from auto_pm.spec.core.registry import SpecRegistry


@dataclass
class IndexOutput:
    generated_files: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class IndexService:
    def __init__(self, workspace: Path, config: WorkspaceConfig | None = None) -> None:
        self.workspace = workspace
        self.config = config or WorkspaceConfig(workspace=workspace)
        self.registry = SpecRegistry(workspace, registry_path=self.config.registry_path)
        if not self.registry.load():
            raise FileNotFoundError(f"注册表文件不存在或格式错误: {self.registry.path}")

    def run(self, domains: list[str] | None = None) -> IndexOutput:
        output = IndexOutput()
        raw = self.registry.raw
        if not raw:
            output.errors.append("注册表为空或不存在")
            return output

        if domains is not None:
            valid_domains = set(DOMAIN_CONFIG.keys()) | {"all"}
            for d in domains:
                if d not in valid_domains:
                    output.errors.append(f"未知规范域: {d}")
            if output.errors:
                return output

        try:
            content = self._generate_global_index(raw)
            output_rel = self.config.output_paths.get("pm_index", DEFAULT_OUTPUT_PATHS["pm_index"])
            output_path = self.workspace / output_rel
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            output.generated_files.append(output_path)
        except Exception as e:
            output.errors.append(f"global_index: {e}")

        return output

    @staticmethod
    def _iter_registry_specs(raw: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
        specs = raw.get("specs", {})
        if not isinstance(specs, dict):
            return []
        return [
            (spec_id, info)
            for spec_id, info in specs.items()
            if isinstance(spec_id, str) and isinstance(info, dict)
        ]

    def _get_specs_by_domain(
        self,
        raw: dict[str, Any],
        domain: str,
        lifecycle_filter: list[str] | None = None,
        existing_order: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if lifecycle_filter is None:
            lifecycle_filter = ["stable", "active", "draft"]
        specs = []
        for spec_id, info in self._iter_registry_specs(raw):
            if info.get("domain") == domain and info.get("lifecycle") in lifecycle_filter:
                entry = dict(info)
                entry["spec_id"] = spec_id
                specs.append(entry)

        if existing_order:
            order_idx = {sid: i for i, sid in enumerate(existing_order)}
            specs.sort(
                key=lambda s: (
                    (0, order_idx[s["spec_id"]])
                    if s["spec_id"] in order_idx
                    else (1, str(s.get("number", "999")), s["spec_id"])
                )
            )
        else:
            specs.sort(key=lambda s: (str(s.get("number", "999")), s["spec_id"]))
        return specs

    def _get_deprecated_specs(
        self,
        raw: dict[str, Any],
        domain: str | None = None,
        lifecycles: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        if lifecycles is None:
            lifecycles = ["deprecated", "archived"]
        specs = []
        for spec_id, info in self._iter_registry_specs(raw):
            domain_match = (domain is None) or (info.get("domain") == domain)
            if domain_match and info.get("lifecycle") in lifecycles:
                entry = dict(info)
                entry["spec_id"] = spec_id
                specs.append(entry)
        specs.sort(key=lambda s: (str(s.get("number", "999")), s["spec_id"]))
        return specs

    def _generate_pm_index(self, raw: dict[str, Any]) -> str:
        """向后兼容别名，直接生成全局规范索引。"""
        return self._generate_global_index(raw)

    def _generate_tech_stack_index(self, raw: dict[str, Any], domain: str) -> str:
        """向后兼容别名，直接生成全局规范索引。"""
        return self._generate_global_index(raw)

    def _generate_global_index(self, raw: dict[str, Any]) -> str:
        output_rel = self.config.output_paths.get("pm_index", DEFAULT_OUTPUT_PATHS["pm_index"])
        existing_path = self.workspace / output_rel
        existing_text = ""
        if existing_path.is_file():
            try:
                existing_text = existing_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                existing_text = ""

        # 提取现有文件中的行内手写描述与既有顺序
        existing_desc: dict[str, str] = {}
        existing_order: list[str] = []
        if existing_text:
            row_re = re.compile(
                r"^\|\s*([A-Z0-9_-]+)\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*[^\|]+\|\s*([^\|]+)\|",
                re.MULTILINE,
            )
            for m in row_re.finditer(existing_text):
                sid = m.group(1).strip()
                existing_order.append(sid)
                desc = m.group(4).strip()
                if desc:
                    existing_desc[sid] = desc

        # 提取手工维护的语义互链清单
        semantic_section = ""
        if existing_text:
            m_sem = re.search(r"(## 🔗 高价值语义互链清单.*?)(?=\n---\n|\Z)", existing_text, re.DOTALL)
            if m_sem:
                semantic_section = m_sem.group(1).strip()

        # 提取手工维护的已归档规范清单
        archived_section = ""
        if existing_text:
            m_arch = re.search(r"(## 已归档规范（Archived）.*?)(?=\n---\n|\Z)", existing_text, re.DOTALL)
            if m_arch:
                archived_section = m_arch.group(1).strip()

        # 提取文件头部已有的修订注记
        rev_notes: list[str] = []
        if existing_text:
            for line in existing_text.splitlines():
                if line.startswith("> **修订注记"):
                    rev_notes.append(line.strip())

        registry_version = raw.get("version", "unknown")
        now = datetime.now().strftime("%Y-%m-%d")

        lines: list[str] = [
            f"# {DOMAIN_CONFIG['pm']['title']} {registry_version}",
            "",
            f"> {AUTO_GENERATED_HEADER}",
            f"> **版本**: {registry_version} (自动生成)",
            f"> **生成日期**: {now}",
            "> **权威来源**: `spec_registry.json` + Obsidian 规范真源文件",
            "> **注册表**: spec_registry.json",
        ]
        for note in rev_notes:
            lines.append(note)
        lines.extend([
            "",
            "---",
            "",
            "## 📋 项目管理域规范",
        ])

        pm_specs = self._get_specs_by_domain(raw, "pm", existing_order=existing_order)
        pm_grouped: dict[str, list[dict[str, Any]]] = {}
        for spec in pm_specs:
            sd = spec.get("sub_domain", "其他")
            pm_grouped.setdefault(sd, []).append(spec)

        pm_cfg = DOMAIN_CONFIG.get("pm", {})
        sub_domain_labels = pm_cfg.get("sub_domains", {})
        rendered_subdomains = set()

        for sub_domain, label in sub_domain_labels.items():
            group_specs = pm_grouped.get(sub_domain, [])
            if not group_specs:
                continue
            rendered_subdomains.add(sub_domain)
            lines.append(f"### {label} ({len(group_specs)}个)")
            lines.append("")
            lines.append("| 编号 | 文件 | 版本 | 说明 |")
            lines.append("|------|------|------|------|")
            for spec in group_specs:
                fname = Path(spec["canonical_path"]).name
                rel = spec["canonical_path"].replace("00_Obsidian_Base全局规范文件仓库/", "")
                desc = existing_desc.get(spec["spec_id"]) or spec.get("title", "")
                lines.append(f"| {spec['spec_id']} | [{fname}]({rel}) | {spec.get('version', '')} | {desc} |")
            lines.append("")

        for sub_domain, group_specs in pm_grouped.items():
            if sub_domain not in rendered_subdomains:
                lines.append(f"### {sub_domain} ({len(group_specs)}个)")
                lines.append("")
                lines.append("| 编号 | 文件 | 版本 | 说明 |")
                lines.append("|------|------|------|------|")
                for spec in group_specs:
                    fname = Path(spec["canonical_path"]).name
                    rel = spec["canonical_path"].replace("00_Obsidian_Base全局规范文件仓库/", "")
                    desc = existing_desc.get(spec["spec_id"]) or spec.get("title", "")
                    lines.append(f"| {spec['spec_id']} | [{fname}]({rel}) | {spec.get('version', '')} | {desc} |")
                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ 技术栈规范真源（PLC / Python / 驾驶舱 / 跨域）")
        lines.append("")

        plc_specs = self._get_specs_by_domain(raw, "plc", existing_order=existing_order)
        python_specs = self._get_specs_by_domain(raw, "python", existing_order=existing_order)
        cockpit_specs = self._get_specs_by_domain(raw, "cockpit", existing_order=existing_order)
        cross_specs = self._get_specs_by_domain(raw, "cross-domain", existing_order=existing_order)

        total_active = len(pm_specs) + len(plc_specs) + len(python_specs) + len(cockpit_specs) + len(cross_specs)
        tech_total = len(plc_specs) + len(python_specs) + len(cockpit_specs) + len(cross_specs)

        lines.append(
            f"> 以下四张域表由 spec_registry.json 驱动生成，数据逐条对齐"
            f"（{len(pm_specs)} 条 PM 域 + {tech_total} 条技术栈域 = {total_active} 条活跃规范全覆盖）。"
        )
        lines.append("")

        def _render_table(specs_list: list[dict[str, Any]]) -> list[str]:
            res: list[str] = [
                "| 编号 | 文件 | 版本 | 说明 |",
                "|------|------|------|------|",
            ]
            for spec in specs_list:
                fname = Path(spec["canonical_path"]).name
                rel = spec["canonical_path"].replace("00_Obsidian_Base全局规范文件仓库/", "")
                desc = existing_desc.get(spec["spec_id"]) or spec.get("title", "")
                res.append(f"| {spec['spec_id']} | [{fname}]({rel}) | {spec.get('version', '')} | {desc} |")
            res.append("")
            return res

        lines.append(f"### 03_PLC 自动化域（LSP/STD/INT/TOOL） ({len(plc_specs)}个)")
        lines.append("")
        lines.extend(_render_table(plc_specs))

        lines.append(f"### 02_Python 开发域（DEV/INT） ({len(python_specs)}个)")
        lines.append("")
        lines.extend(_render_table(python_specs))

        lines.append(f"### 04_驾驶舱与全栈域（DEV/STD） ({len(cockpit_specs)}个)")
        lines.append("")
        lines.extend(_render_table(cockpit_specs))

        lines.append(f"### 05_跨域工具规范 + 跨域 DEV（TOOL/DEV） ({len(cross_specs)}个)")
        lines.append("")
        lines.extend(_render_table(cross_specs))

        lines.append("**冲突处理**: 当全局PM规范与技术栈编码/架构规范冲突时，以本索引列出的技术栈真源目录为准")
        lines.append("")
        lines.append("---")
        lines.append("")

        if semantic_section:
            lines.append(semantic_section)
            lines.append("")
            lines.append("---")
            lines.append("")

        deprecated_specs = self._get_deprecated_specs(raw, domain=None, lifecycles=["deprecated"])
        lines.append("## 已废弃规范（Deprecated）")
        lines.append("")
        lines.append("> 以下规范已被替代，仅供历史参考")
        lines.append("")
        if deprecated_specs:
            lines.append("| spec_id | 标题 | 替代规范 | 废弃日期 |")
            lines.append("|---------|------|---------|---------|")
            for spec in deprecated_specs:
                replaced_by = spec.get("replaced_by", [])
                replaced_str = ", ".join(replaced_by) if isinstance(replaced_by, list) else str(replaced_by)
                deprecated_date = spec.get("deprecated_date", "未知")
                lines.append(
                    f"| {spec['spec_id']} | {spec.get('title', '')} | {replaced_str or '无'} | {deprecated_date} |"
                )
        else:
            lines.append("暂无")
        lines.append("")

        if archived_section:
            lines.append(archived_section)
            lines.append("")
            lines.append("---")
            lines.append("")
            archived_count = len(re.findall(r"^\|\s*[A-Z0-9_-]+\s*\|", archived_section, re.MULTILINE))
        else:
            archived_specs = self._get_deprecated_specs(raw, domain=None, lifecycles=["archived"])
            lines.append("## 已归档规范（Archived）")
            lines.append("")
            lines.append("> 以下规范已从活跃目录移除")
            lines.append("")
            if archived_specs:
                lines.append("| spec_id | 标题 | 归档路径 | 归档日期 |")
                lines.append("|---------|------|---------|---------|")
                for spec in archived_specs:
                    canonical_path = spec.get("canonical_path", "")
                    archived_date = spec.get("archived_date", "未知")
                    lines.append(f"| {spec['spec_id']} | {spec.get('title', '')} | {canonical_path} | {archived_date} |")
            else:
                lines.append("暂无")
            lines.append("")
            lines.append("---")
            lines.append("")
            archived_count = len(archived_specs)

        lines.append("## 📊 统计")
        lines.append("")
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 活跃PM规范 | **{len(pm_specs)}个** |")
        lines.append(f"| PLC自动化域 | **{len(plc_specs)}个** |")
        lines.append(f"| Python开发域 | **{len(python_specs)}个** |")
        lines.append(f"| 驾驶舱与全栈域 | **{len(cockpit_specs)}个** |")
        lines.append(f"| 跨域通用 | **{len(cross_specs)}个** |")
        lines.append(f"| 活跃规范合计 | **{total_active}个** |")
        lines.append(f"| 已废弃规范 | **{len(deprecated_specs)}个** |")
        lines.append(f"| 已归档规范 | **{archived_count}个** |")
        lines.append(f"| 最后更新 | {now} |")
        lines.append("")
        lines.append(f"*索引自动生成: {now} | 注册表版本: {registry_version}*")

        return "\n".join(lines)
