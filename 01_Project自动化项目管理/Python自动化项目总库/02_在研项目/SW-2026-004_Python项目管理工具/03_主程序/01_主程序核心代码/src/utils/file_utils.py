# -*- coding: utf-8 -*-
"""
文件操作工具
"""
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .logger import setup_logger

logger = setup_logger(__name__)

def read_json(file_path: Union[str, Path], default: Any = None) -> Optional[Dict[str, Any]]:
    """读取JSON文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取JSON文件失败 {file_path}: {e}")
        return default

def write_json(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 4) -> bool:
    """写入JSON文件"""
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败 {file_path}: {e}")
        return False

def read_file(file_path: Union[str, Path], default: str = "") -> str:
    """读取文本文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return default

def write_file(file_path: Union[str, Path], content: str) -> bool:
    """写入文本文件"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"写入文件失败 {file_path}: {e}")
        return False

def copy_file(source: Union[str, Path], target: Union[str, Path], overwrite: bool = False) -> bool:
    """复制文件"""
    try:
        source_path = Path(source)
        target_path = Path(target)
        
        if not source_path.exists():
            logger.error(f"源文件不存在: {source}")
            return False
        
        if target_path.exists() and not overwrite:
            logger.warning(f"目标文件已存在，跳过复制: {target}")
            return True
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        return True
    except Exception as e:
        logger.error(f"复制文件失败 {source} -> {target}: {e}")
        return False

def copy_directory(source: Union[str, Path], target: Union[str, Path], overwrite: bool = False) -> bool:
    """复制目录"""
    try:
        source_path = Path(source)
        target_path = Path(target)
        
        if not source_path.exists() or not source_path.is_dir():
            logger.error(f"源目录不存在: {source}")
            return False
        
        if target_path.exists():
            if overwrite:
                shutil.rmtree(target_path)
            else:
                logger.warning(f"目标目录已存在，跳过复制: {target}")
                return True
        
        shutil.copytree(source_path, target_path)
        return True
    except Exception as e:
        logger.error(f"复制目录失败 {source} -> {target}: {e}")
        return False

def delete_file(file_path: Union[str, Path]) -> bool:
    """删除文件"""
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            path.unlink()
        return True
    except Exception as e:
        logger.error(f"删除文件失败 {file_path}: {e}")
        return False

def delete_directory(dir_path: Union[str, Path]) -> bool:
    """删除目录"""
    try:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
        return True
    except Exception as e:
        logger.error(f"删除目录失败 {dir_path}: {e}")
        return False

def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return 0

def get_directory_size(dir_path: Union[str, Path]) -> int:
    """获取目录大小（字节）"""
    total_size = 0
    try:
        for path in Path(dir_path).rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size
    except Exception as e:
        # 修复P2-#18: 记录异常日志，避免静默吞没异常
        logger.warning(f"获取目录大小失败: {dir_path}, 错误: {e}")
    return total_size
