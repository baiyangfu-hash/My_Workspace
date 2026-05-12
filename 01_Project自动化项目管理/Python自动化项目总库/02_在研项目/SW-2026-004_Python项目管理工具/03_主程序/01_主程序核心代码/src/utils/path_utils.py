# -*- coding: utf-8 -*-
"""
路径处理工具
"""
import os
import re
from pathlib import Path
from typing import Optional, Union

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    # 移除Windows非法字符
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_chars, "", filename)
    # 限制长度
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255 - len(ext)] + ext
    return sanitized

def get_project_path(base_path: Union[str, Path], project_code: str, project_name: str) -> Path:
    """生成项目路径"""
    sanitized_name = sanitize_filename(project_name)
    dir_name = f"{project_code}_{sanitized_name}"
    return Path(base_path) / dir_name

def ensure_directory(path: Union[str, Path]) -> tuple[bool, str]:
    """
    确保目录存在，如果不存在则创建

    Returns:
        (成功标志, 错误信息) 元组
        - 成功时返回 (True, "")
        - 失败时返回 (False, 具体错误原因)
    """
    from src.utils.logger import setup_logger
    logger = setup_logger(__name__)

    try:
        path_obj = Path(path)

        # 检查路径长度（Windows 限制 260 字符）
        if len(str(path_obj)) > 260:
            error_msg = f"路径过长（{len(str(path_obj))}字符），超过 Windows 260 字符限制"
            logger.error(f"目录创建失败: {error_msg}, 路径: {path}")
            return False, error_msg

        # 尝试创建目录
        path_obj.mkdir(parents=True, exist_ok=True)

        # 验证目录确实存在且可写
        if not path_obj.exists():
            return False, "目录创建后仍不存在"

        # 测试可写性
        test_file = path_obj / ".write_test_tmp"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as write_error:
            return False, f"目录不可写: {str(write_error)}"

        return True, ""

    except PermissionError as e:
        error_msg = f"权限不足: 无法创建目录 '{path}'"
        logger.exception(f"权限不足: {error_msg}")
        return False, error_msg
    except FileNotFoundError as e:
        error_msg = f"路径不存在或无效: '{path}'"
        logger.exception(f"路径不存在: {error_msg}")
        return False, error_msg
    except OSError as e:
        if "No space left" in str(e):
            error_msg = "磁盘空间不足"
        else:
            error_msg = f"操作系统错误: {str(e)}"
        logger.exception(f"OS错误: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        logger.exception(f"目录创建失败: {error_msg}")
        return False, error_msg

def is_empty_directory(path: Union[str, Path]) -> bool:
    """检查目录是否为空"""
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return False
    return not any(path.iterdir())

def get_relative_path(base_path: Union[str, Path], target_path: Union[str, Path]) -> Optional[str]:
    """获取相对路径"""
    try:
        return str(Path(target_path).relative_to(base_path))
    except ValueError:
        return None

def normalize_path(path: Union[str, Path]) -> str:
    """标准化路径格式，统一使用正斜杠"""
    return str(Path(path)).replace("\\", "/")

def get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写）"""
    return Path(filename).suffix.lower()
