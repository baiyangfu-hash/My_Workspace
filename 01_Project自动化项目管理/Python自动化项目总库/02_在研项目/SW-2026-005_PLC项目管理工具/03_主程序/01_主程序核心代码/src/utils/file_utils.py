# -*- coding: utf-8 -*-
"""
文件工具模块

提供文件操作相关的通用工具函数。
包括安全读写、路径处理、编码检测等功能。
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def ensure_directory(path: str) -> Path:
    """
    确保目录存在，不存在则递归创建

    Args:
        path: 目录路径字符串

    Returns:
        Path: 目录Path对象
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_read_text(file_path: str, encoding: str = "utf-8") -> Tuple[Optional[str], Optional[str]]:
    """
    安全读取文本文件（带异常处理）

    Args:
        file_path: 文件路径
        encoding: 编码格式，默认utf-8

    Returns:
        Tuple[Optional[str], Optional[str]]: (文件内容或None, 错误信息或None)
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None, f"文件不存在: {file_path}"

        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        return content, None
    except UnicodeDecodeError as e:
        # 尝试其他常见编码
        for fallback_enc in ["gbk", "gb2312", "latin-1"]:
            try:
                with open(file_path, "r", encoding=fallback_enc) as f:
                    return f.read(), f"使用{fallback_enc}}编码读取"
            except Exception:
                continue
        return None, f"编码错误: {e}"
    except IOError as e:
        return None, f"文件读取失败: {e}"


def safe_write_text(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> Tuple[bool, Optional[str]]:
    """
    安全写入文本文件（带异常处理和目录自动创建）

    Args:
        file_path: 目标文件路径
        content: 要写入的内容
        encoding: 编码格式
        create_dirs: 是否自动创建父目录

    Returns:
        Tuple[bool, Optional[str]]: (是否成功, 错误信息或None)
    """
    try:
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding=encoding) as f:
            f.write(content)

        return True, None
    except IOError as e:
        logger.error(f"文件写入失败 [{file_path}]: {e}")
        return False, str(e)


def copy_file_with_backup(src: str, dst: str) -> Tuple[bool, Optional[str]]:
    """
    复制文件并在目标位置保留备份

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        Tuple[bool, Optional[str]]: (是否成功, 错误信息或None)
    """
    try:
        dst_path = Path(dst)
        if dst_path.exists():
            backup_path = dst_path.with_suffix(
                dst_path.suffix + ".bak"
            )
            shutil.copy2(str(dst_path), str(backup_path))
            logger.debug(f"已创建备份: {backup_path}")

        shutil.copy2(src, dst)
        return True, None
    except (IOError, shutil.Error) as e:
        return False, str(e)


def find_files_by_pattern(
    directory: str,
    pattern: str = "*",
    recursive: bool = True,
) -> List[Path]:
    """
    在目录中按模式查找文件

    Args:
        directory: 搜索根目录
        pattern: glob匹配模式 (如 "*.md", "*.st")
        recursive: 是否递归搜索子目录

    Returns:
        List[Path]: 匹配的文件路径列表
    """
    base_dir = Path(directory)
    if not base_dir.exists():
        return []

    if recursive:
        return sorted(base_dir.rglob(pattern))
    else:
        return sorted(base_dir.glob(pattern))


def get_file_size_str(file_path: str) -> str:
    """获取人类可读的文件大小字符串"""
    path = Path(file_path)
    if not path.exists():
        return "N/A"

    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def clean_directory(directory: str, keep_patterns: List[str] = None) -> int:
    """
    清理目录中的临时/缓存文件

    Args:
        directory: 目标目录
        keep_patterns: 保留的文件模式列表

    Returns:
        int: 删除的文件数量
    """
    default_clean_patterns = [
        "__pycache__", "*.pyc", ".DS_Store", "Thumbs.db",
        "*.tmp", "*.bak", "*~",
    ]
    patterns = keep_patterns or default_clean_patterns

    deleted_count = 0
    base_dir = Path(directory)

    if not base_dir.exists():
        return 0

    for pattern in patterns:
        for item in base_dir.rglob(pattern):
            try:
                if item.is_file():
                    item.unlink()
                    deleted_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted_count += 1
            except OSError as e:
                logger.warning(f"清理失败 [{item}]: {e}")

    if deleted_count > 0:
        logger.info(f"已清理 {deleted_count} 个文件/目录于: {directory}")

    return deleted_count
