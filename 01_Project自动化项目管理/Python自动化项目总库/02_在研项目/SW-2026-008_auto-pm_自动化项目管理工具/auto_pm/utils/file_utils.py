"""文件操作工具"""

from __future__ import annotations

import os
import tempfile


def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """读取文件内容，失败返回空字符串"""
    try:
        with open(file_path, encoding=encoding) as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """原子写入文件内容，自动创建父目录

    使用"写入临时文件 → os.replace 替换"模式确保原子性（TD-T11 修复）：
    - 写入过程中中断不会损坏原文件（原文件保持不变）
    - os.replace 在 Windows 和 POSIX 上都是原子操作
    - 临时文件与目标文件在同一目录（确保 os.replace 可用）

    Args:
        file_path: 目标文件路径
        content: 文件内容
        encoding: 文件编码，默认 utf-8
    """
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # 在同目录创建临时文件（os.replace 要求源和目标在同一文件系统）
    fd, tmp_path = tempfile.mkstemp(dir=dir_path or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, file_path)
    except Exception:
        # 写入失败时清理临时文件，原文件不受影响
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_mtime(file_path: str) -> float:
    """获取文件修改时间，失败返回0"""
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0.0
