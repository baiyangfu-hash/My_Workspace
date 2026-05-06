# -*- coding: utf-8 -*-
"""
配置管理模块

提供全局配置的加载、读取、修改和持久化功能。
采用单例模式管理配置状态，支持JSON文件加载和默认值回退。
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """
    全局配置管理器 (单例模式)

    使用方式:
        ConfigLoader.load()           # 加载配置
        ConfigLoader.get("app_name")  # 读取配置项
        ConfigLoader.set("key", val)  # 设置配置项
        ConfigLoader.save()           # 持久化到文件
    """

    _config: Dict[str, Any] = {}
    _config_dir: Optional[Path] = None
    _loaded: bool = False

    @classmethod
    def load(cls, custom_config_path: Optional[str] = None):
        """
        加载配置文件

        Args:
            custom_config_path: 自定义配置文件路径，为None时使用默认路径
        """
        if custom_config_path:
            config_path = Path(custom_config_path)
            cls._config_dir = config_path.parent
        else:
            cls._config_dir = Path(__file__).parent.parent.parent / "config"
            config_path = cls._config_dir / "app_config.json"

        # 尝试从文件加载配置
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cls._config = json.load(f)
                logger = _get_fallback_logger()
                logger.debug(f"配置文件已加载: {config_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger = _get_fallback_logger()
                logger.warning(f"配置文件加载失败，使用默认配置: {e}")
                cls._config = cls._get_default_config()
        else:
            cls._config = cls._get_default_config()

        cls._loaded = True

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置字典"""
        return {
            "app_name": "SW-2026-005 PLC项目管理工具",
            "version": "1.0.0",
            "author": "Trae AI",
            "default_project_root": "./Projects",
            "language": "zh-CN",
            "theme": "light",
            "auto_backup": True,
            "backup_interval": 3600,
            "debug_mode": False,
            "editor": {
                "font_family": "Consolas",
                "font_size": 12,
                "tab_width": 4,
                "show_line_numbers": True,
            },
            "plc": {
                "default_brand": "Codesys",
                "supported_languages": ["ST", "LD", "FBD", "SFC"],
            },
            "database": {
                "db_type": "sqlite",
                "db_name": "plc_project_manager.db",
            },
        }

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置项（支持点号分隔的嵌套键）

        Args:
            key: 配置键名，如 "editor.font_size"
            default: 键不存在时的默认返回值

        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = cls._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @classmethod
    def set(cls, key: str, value: Any):
        """
        设置配置项（支持点号分隔的嵌套键）

        Args:
            key: 配置键名
            value: 要设置的值
        """
        keys = key.split(".")
        config = cls._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    @classmethod
    def save(cls):
        """将当前配置保存到JSON文件"""
        if not cls._config_dir:
            raise RuntimeError("配置目录未初始化，请先调用 load()")

        cls._config_dir.mkdir(parents=True, exist_ok=True)
        save_path = cls._config_dir / "app_config.json"

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cls._config, f, indent=4, ensure_ascii=False)

        logger = _get_fallback_logger()
        logger.info(f"配置已保存至: {save_path}")

    @classmethod
    def get_config_dir(cls) -> Path:
        """获取配置目录路径"""
        if cls._config_dir is None:
            cls._config_dir = (
                Path(__file__).parent.parent.parent / "config"
            )
        return cls._config_dir

    @classmethod
    def get_data_dir(cls) -> Path:
        """获取数据存储目录路径"""
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @classmethod
    def is_loaded(cls) -> bool:
        """检查配置是否已加载"""
        return cls._loaded


def _get_fallback_logger():
    """获取备用日志记录器（避免循环导入）"""
    import logging
    return logging.getLogger("ConfigLoader")
