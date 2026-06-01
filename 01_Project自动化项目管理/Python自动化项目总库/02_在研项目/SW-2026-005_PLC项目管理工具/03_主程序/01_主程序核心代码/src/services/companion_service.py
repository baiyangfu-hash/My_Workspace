# -*- coding: utf-8 -*-
"""
Trae伴生跳转服务

集中管理本工具与Trae IDE之间的交互边界。
本工具定位为Trae伴生式治理工具, 职责范围:
- 挂载(mount): 加载工作空间与子项目
- 索引(index): 扫描资产与构建目录
- 检查(check): 规范检查与诊断
- 汇总(summarize): 聚合报告与统计
- 导出(export): Excel/报告输出

不负责:
- 源码编辑(edit_source)
- 编译(compile)
- 部署(deploy)
- 运行时调试(debug_runtime)
"""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from src.core.constants import (
    COMPANION_CAPABILITIES,
    COMPANION_NON_CAPABILITIES,
    COMPANION_PRIMARY_IDE,
    COMPANION_ROLE,
    TRAJUMP_SUPPORTED_EXTENSIONS,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CompanionService:
    """Trae伴生跳转服务

    职责:
    1. 判断文件是否应跳转到Trae处理
    2. 执行跳转(通过系统调用打开Trae或默认编辑器)
    3. 记录跳转日志
    4. 提供伴生能力边界查询
    """

    @classmethod
    def can_handle(cls, capability: str) -> bool:
        """判断本工具是否具备指定能力

        Args:
            capability: 能力标识, 如 "edit_source", "check" 等

        Returns:
            bool
        """
        if capability in COMPANION_CAPABILITIES:
            return True
        if capability in COMPANION_NON_CAPABILITIES:
            return False
        return False

    @classmethod
    def should_jump_to_ide(cls, file_path: str) -> bool:
        """判断文件是否应跳转到Trae处理

        规则:
        - 源码文件(.scl/.st/.plc) -> 跳转
        - 配置文件(.xml/.json/.yaml) -> 跳转
        - 文档文件(.md/.txt) -> 跳转
        - 二进制文件 -> 不跳转(本工具无法处理, 但也不应跳转到编辑器)

        Args:
            file_path: 文件路径

        Returns:
            bool
        """
        ext = Path(file_path).suffix.lower()
        return ext in TRAJUMP_SUPPORTED_EXTENSIONS

    @classmethod
    def jump_to_file(
        cls, file_path: str, line_number: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """跳转到Trae或系统默认编辑器打开文件

        Args:
            file_path: 目标文件路径
            line_number: 目标行号(0表示不指定)

        Returns:
            Tuple[bool, str|None]: (是否成功, 错误信息)
        """
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"

        ext = Path(file_path).suffix.lower()

        if ext in {".scl", ".st", ".plc"}:
            result = cls._open_in_trae(file_path, line_number)
            if result[0]:
                return result
            logger.info(f"Trae跳转失败, 降级到系统默认: {result[1]}")
            return cls._open_with_system(file_path)

        if ext in {".xlsx", ".xls"}:
            return cls._open_with_system(file_path)

        return cls._open_with_system(file_path)

    @classmethod
    def _open_in_trae(
        cls, file_path: str, line_number: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """尝试通过Trae CLI打开文件

        Args:
            file_path: 文件路径
            line_number: 行号

        Returns:
            Tuple[bool, str|None]
        """
        try:
            cmd = ["trae", file_path]
            if line_number > 0:
                cmd.extend(["--goto", str(line_number)])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"Trae跳转成功: {file_path}:{line_number}")
                return True, None
            else:
                return False, f"Trae返回非零退出码: {result.returncode}"

        except FileNotFoundError:
            return False, "Trae CLI未安装或不在PATH中"
        except subprocess.TimeoutExpired:
            return False, "Trae跳转超时"
        except Exception as e:
            return False, f"Trae跳转异常: {e}"

    @classmethod
    def _open_with_system(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        """使用系统默认程序打开文件

        Args:
            file_path: 文件路径

        Returns:
            Tuple[bool, str|None]
        """
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":
                subprocess.run(["open", file_path], check=True)
            else:
                subprocess.run(["xdg-open", file_path], check=True)

            logger.info(f"系统默认打开: {file_path}")
            return True, None

        except Exception as e:
            return False, f"系统打开失败: {e}"

    @classmethod
    def get_role_description(cls) -> str:
        """获取伴生角色描述"""
        return (
            f"本工具是{COMPANION_PRIMARY_IDE}的伴生式治理工具, "
            f"角色: {COMPANION_ROLE}, "
            f"能力: {', '.join(COMPANION_CAPABILITIES)}, "
            f"不负责: {', '.join(COMPANION_NON_CAPABILITIES)}"
        )

    @classmethod
    def get_jump_summary(cls) -> dict:
        """获取跳转统计摘要(用于Dashboard展示)"""
        return {
            "role": COMPANION_ROLE,
            "primary_ide": COMPANION_PRIMARY_IDE,
            "capabilities": COMPANION_CAPABILITIES,
            "non_capabilities": COMPANION_NON_CAPABILITIES,
            "supported_extensions": sorted(TRAJUMP_SUPPORTED_EXTENSIONS),
        }
