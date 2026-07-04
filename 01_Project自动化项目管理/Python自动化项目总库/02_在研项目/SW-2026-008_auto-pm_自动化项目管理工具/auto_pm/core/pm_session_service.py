"""PM_SESSION 解析/归档/检查服务

提供 PM_SESSION_SW-2026-008.md 文件的章节级解析、归档和健康检查能力。

三层真源架构（CHG-087 Stage 1 建立，CHG-088 Stage 2 自动化）：
1. Active 主文件：保留最新迭代状态
2. Historical 归档：archive_V*.md 完整保留历史
3. Event 实体：CHG-*.md 变更单
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

# 章节标题正则：## N. Title（N 为数字）
SECTION_HEADER_PATTERN = re.compile(r"^##\s+(\d+)\.\s+(.+)$")

# 健康检查阈值（CHG-087 Stage 1 基线：170 行 / 62KB）
MAX_FILE_SIZE_KB = 150  # 主文件最大 150KB
MAX_FILE_LINES = 300  # 主文件最大 300 行

# 必须存在的章节（Stage 1 后基线，§7 已归档删除）
REQUIRED_SECTIONS = {"0", "1", "2", "3", "4", "5", "6", "8", "9"}
# §7 应该不存在（已归档）
DEPRECATED_SECTIONS = {"7"}

# 归档目录约定
ARCHIVE_DIR_NAME = "05_PM_SESSION归档"
ARCHIVE_DIR_PARENT = "00_项目管理"
ARCHIVE_FILE_PATTERN = "PM_SESSION_{project_id}_archive_{version}.md"


@dataclass
class PmSessionSection:
    """PM_SESSION 章节"""

    number: str  # "0", "1", ..., "9"
    title: str  # "Meta", "Positioning（项目定位）", ...
    start_line: int  # 0-based 行号（header 行）
    end_line: int  # 0-based 行号（exclusive）
    header_line: str  # "## 0. Meta"
    content: str  # 章节内容（不含 header 行）

    @property
    def line_count(self) -> int:
        """章节总行数（含 header）"""
        return self.end_line - self.start_line


@dataclass
class PmSessionParseResult:
    """PM_SESSION 解析结果"""

    file_path: Path
    total_lines: int
    sections: list[PmSessionSection]
    pre_header_lines: list[str] = field(default_factory=list)  # 章节标题之前的行

    def get_section(self, number: str) -> PmSessionSection | None:
        """按章节号获取章节"""
        for s in self.sections:
            if s.number == number:
                return s
        return None

    def find_missing_required(self) -> set[str]:
        """查找缺失的必须章节"""
        existing = {s.number for s in self.sections}
        return REQUIRED_SECTIONS - existing

    def find_deprecated_present(self) -> set[str]:
        """查找不应存在的已归档章节"""
        existing = {s.number for s in self.sections}
        return existing & DEPRECATED_SECTIONS


@dataclass
class CheckResult:
    """健康检查结果"""

    file_path: Path
    file_size_kb: float
    total_lines: int
    missing_required: set[str]
    deprecated_present: set[str]
    is_oversized: bool
    warnings: list[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        """是否健康（无缺失章节 + 无已归档章节回归 + 未超规模）"""
        return (
            not self.missing_required
            and not self.deprecated_present
            and not self.is_oversized
        )


@dataclass
class ArchiveResult:
    """归档结果"""

    archive_file: Path
    archived_sections: list[str]  # 归档的章节号
    archived_line_count: int
    main_file_lines_before: int
    main_file_lines_after: int
    backup_file: Path | None = None


class PmSessionParser:
    """PM_SESSION 章节级解析器"""

    def parse_file(self, file_path: Path) -> PmSessionParseResult:
        """解析 PM_SESSION 文件

        Args:
            file_path: PM_SESSION 文件路径

        Returns:
            PmSessionParseResult
        """
        content = file_path.read_text(encoding="utf-8")
        return self.parse_content(content, file_path)

    def parse_content(self, content: str, file_path: Path | None = None) -> PmSessionParseResult:
        """解析 PM_SESSION 内容字符串

        Args:
            content: PM_SESSION markdown 内容
            file_path: 文件路径（仅用于结果标记）

        Returns:
            PmSessionParseResult
        """
        lines = content.splitlines(keepends=False)
        sections: list[PmSessionSection] = []
        pre_header_lines: list[str] = []

        current_section: PmSessionSection | None = None

        for i, line in enumerate(lines):
            match = SECTION_HEADER_PATTERN.match(line)
            if match:
                # 保存前一个章节
                if current_section is not None:
                    current_section.end_line = i
                    current_section.content = "\n".join(
                        lines[current_section.start_line + 1 : i]
                    )
                    sections.append(current_section)

                # 开始新章节
                section_number = match.group(1)
                section_title = match.group(2).strip()
                current_section = PmSessionSection(
                    number=section_number,
                    title=section_title,
                    start_line=i,
                    end_line=-1,
                    header_line=line,
                    content="",
                )
            elif current_section is None:
                pre_header_lines.append(line)

        # 保存最后一个章节
        if current_section is not None:
            current_section.end_line = len(lines)
            current_section.content = "\n".join(
                lines[current_section.start_line + 1 : len(lines)]
            )
            sections.append(current_section)

        return PmSessionParseResult(
            file_path=file_path or Path(),
            total_lines=len(lines),
            sections=sections,
            pre_header_lines=pre_header_lines,
        )


class PmSessionCheckService:
    """PM_SESSION 健康检查服务"""

    def __init__(self, parser: PmSessionParser | None = None) -> None:
        self.parser = parser or PmSessionParser()

    def check(self, file_path: Path) -> CheckResult:
        """检查 PM_SESSION 文件健康状态

        Args:
            file_path: PM_SESSION 文件路径

        Returns:
            CheckResult
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PM_SESSION 文件不存在: {file_path}")

        result = self.parser.parse_file(file_path)
        file_size = file_path.stat().st_size
        file_size_kb = file_size / 1024.0

        missing_required = result.find_missing_required()
        deprecated_present = result.find_deprecated_present()
        is_oversized = file_size_kb > MAX_FILE_SIZE_KB or result.total_lines > MAX_FILE_LINES

        warnings: list[str] = []
        if missing_required:
            warnings.append(f"缺失必须章节: {sorted(missing_required)}")
        if deprecated_present:
            warnings.append(f"已归档章节回归: {sorted(deprecated_present)}")
        if file_size_kb > MAX_FILE_SIZE_KB:
            warnings.append(
                f"文件大小 {file_size_kb:.1f}KB 超过阈值 {MAX_FILE_SIZE_KB}KB"
            )
        if result.total_lines > MAX_FILE_LINES:
            warnings.append(
                f"文件行数 {result.total_lines} 超过阈值 {MAX_FILE_LINES}"
            )

        return CheckResult(
            file_path=file_path,
            file_size_kb=round(file_size_kb, 1),
            total_lines=result.total_lines,
            missing_required=missing_required,
            deprecated_present=deprecated_present,
            is_oversized=is_oversized,
            warnings=warnings,
        )


class PmSessionArchiveService:
    """PM_SESSION 归档服务

    将指定章节的早期内容移动到归档文件，主文件保留最新内容 + 归档索引。
    """

    def __init__(self, parser: PmSessionParser | None = None) -> None:
        self.parser = parser or PmSessionParser()

    def archive_section(
        self,
        main_file: Path,
        archive_file: Path,
        section_number: str,
        keep_recent: int = 0,
        create_backup: bool = True,
    ) -> ArchiveResult:
        """归档指定章节

        Args:
            main_file: PM_SESSION 主文件路径
            archive_file: 归档文件路径
            section_number: 要归档的章节号（如 "6"）
            keep_recent: 主文件保留该章节最近 N 行内容（0=整章归档）
            create_backup: 是否创建主文件备份

        Returns:
            ArchiveResult
        """
        if not main_file.exists():
            raise FileNotFoundError(f"PM_SESSION 主文件不存在: {main_file}")

        parse_result = self.parser.parse_file(main_file)
        section = parse_result.get_section(section_number)
        if section is None:
            raise ValueError(f"章节 §{section_number} 不存在于 {main_file}")

        main_lines_before = parse_result.total_lines
        backup_file: Path | None = None

        if create_backup:
            backup_file = main_file.with_suffix(main_file.suffix + ".bak_archive")
            shutil.copy2(main_file, backup_file)

        # 计算要归档的行范围
        # 章节结构：[start_line]=header, [start_line+1, end_line)=content
        section_total_lines = section.end_line - section.start_line
        content_lines = section_total_lines - 1  # 不含 header
        if keep_recent >= content_lines:
            # 保留行数 >= 内容行数，无需归档
            return ArchiveResult(
                archive_file=archive_file,
                archived_sections=[section_number],
                archived_line_count=0,
                main_file_lines_before=main_lines_before,
                main_file_lines_after=main_lines_before,
                backup_file=backup_file,
            )

        lines_to_archive = main_file.read_text(encoding="utf-8").splitlines(keepends=False)

        if keep_recent == 0:
            # 整章归档（包括 header）：主文件删除整个章节
            archived_content_lines = lines_to_archive[section.start_line : section.end_line]
            archived_content = "\n".join(archived_content_lines)
            # 主文件：删除整个章节
            new_main_lines = (
                lines_to_archive[: section.start_line]
                + lines_to_archive[section.end_line :]
            )
        else:
            # 保留 header + 最后 keep_recent 行内容
            archive_end = section.end_line - keep_recent
            archived_content_lines = lines_to_archive[section.start_line + 1 : archive_end]
            # 归档内容：header 副本（方便归档文件识别章节）+ 归档的内容行
            archived_content = section.header_line + "\n" + "\n".join(archived_content_lines)
            # 主文件：保留 header 行 + 最后 keep_recent 行内容
            new_main_lines = (
                lines_to_archive[: section.start_line + 1]  # 保留到 header 行（含）
                + lines_to_archive[archive_end:]  # 保留最后 keep_recent 行
            )

        # 追加到归档文件
        archive_file.parent.mkdir(parents=True, exist_ok=True)
        if archive_file.exists():
            existing = archive_file.read_text(encoding="utf-8")
            archive_file.write_text(
                existing.rstrip("\n") + "\n\n" + archived_content + "\n",
                encoding="utf-8",
            )
        else:
            # 新建归档文件，添加标题
            header = "# PM_SESSION 归档\n\n> 由 auto-pm pm-session archive 自动生成\n\n"
            archive_file.write_text(
                header + archived_content + "\n", encoding="utf-8"
            )

        # 重写主文件
        main_file.write_text(
            "\n".join(new_main_lines) + "\n", encoding="utf-8"
        )

        # 验证重写后的行数
        new_parse = self.parser.parse_file(main_file)

        return ArchiveResult(
            archive_file=archive_file,
            archived_sections=[section_number],
            archived_line_count=len(archived_content_lines),
            main_file_lines_before=main_lines_before,
            main_file_lines_after=new_parse.total_lines,
            backup_file=backup_file,
        )


def generate_view(parse_result: PmSessionParseResult) -> str:
    """从 PM_SESSION 解析结果生成只读视图

    提取 §2 Current Focus + §3 Status Summary，生成简洁的只读 markdown 视图。

    Args:
        parse_result: PM_SESSION 解析结果

    Returns:
        只读视图 markdown 字符串
    """
    lines: list[str] = [
        "# PM_SESSION 只读视图",
        "",
        f"> 源文件: {parse_result.file_path}",
        f"> 总行数: {parse_result.total_lines}",
        f"> 章节数: {len(parse_result.sections)}",
        "",
    ]

    # §2 Current Focus
    section_2 = parse_result.get_section("2")
    if section_2:
        lines.append(f"## §2 {section_2.title}")
        lines.append("")
        lines.append(section_2.content.rstrip())
        lines.append("")

    # §3 Status Summary
    section_3 = parse_result.get_section("3")
    if section_3:
        lines.append(f"## §3 {section_3.title}")
        lines.append("")
        lines.append(section_3.content.rstrip())
        lines.append("")

    # §9 Next Actions
    section_9 = parse_result.get_section("9")
    if section_9:
        lines.append(f"## §9 {section_9.title}")
        lines.append("")
        lines.append(section_9.content.rstrip())
        lines.append("")

    return "\n".join(lines)
