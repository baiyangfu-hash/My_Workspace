# -*- coding: utf-8 -*-
"""
Settings管理器

管理用户偏好设置和应用运行时状态。
包括主题切换、编辑器参数、窗口布局记忆等功能。
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import ConfigLoader


class SettingsManager:
    """
    用户设置管理器

    管理用户的个性化配置，独立于全局ConfigLoader。
    设置保存在用户数据目录下的 settings.json 文件中。
    """

    _settings: Dict[str, Any] = {}
    _settings_path: Optional[Path] = None

    # 默认设置值
    DEFAULTS = {
        "theme": "light",
        "language": "zh-CN",
        "window_geometry": None,
        "window_state": None,
        "recent_projects": [],
        "max_recent_projects": 10,
        "editor_font_family": "Consolas",
        "editor_font_size": 12,
        "editor_tab_width": 4,
        "editor_show_line_numbers": True,
        "editor_auto_indent": True,
        "editor_word_wrap": False,
        "plc_default_brand": "Codesys",
        "hmi_default_brand": "Weinview",
        "auto_save_interval": 300,
        "auto_backup": True,
        "show_startup_dashboard": True,
        "sidebar_width": 220,
    }

    @classmethod
    def initialize(cls, settings_dir: Optional[Path] = None):
        """
        初始化设置管理器

        Args:
            settings_dir: 自定义设置目录，默认使用数据目录
        """
        if settings_dir:
            cls._settings_path = settings_dir / "settings.json"
        else:
            data_dir = ConfigLoader.get_data_dir()
            cls._settings_path = data_dir / "settings.json"

        cls._load()

    @classmethod
    def _load(cls):
        """从文件加载设置"""
        if cls._settings_path and cls._settings_path.exists():
            try:
                with open(cls._settings_path, "r", encoding="utf-8") as f:
                    cls._settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                cls._settings = {}
        else:
            cls._settings = {}

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取设置项

        Args:
            key: 设置键名
            default: 默认值（优先使用DEFAULTS中的值）

        Returns:
            设置值
        """
        if default is None:
            default = cls.DEFAULTS.get(key)
        return cls._settings.get(key, default)

    @classmethod
    def set(cls, key: str, value: Any):
        """
        设置配置项

        Args:
            key: 设置键名
            value: 设置值
        """
        cls._settings[key] = value

    @classmethod
    def save(cls):
        """保存设置到文件"""
        if not cls._settings_path:
            return

        cls._settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cls._settings_path, "w", encoding="utf-8") as f:
            json.dump(cls._settings, f, indent=4, ensure_ascii=False)

    @classmethod
    def add_recent_project(cls, project_path: str, project_name: str):
        """
        添加最近打开的项目

        Args:
            project_path: 项目路径
            project_name: 项目名称
        """
        recent = cls.get("recent_projects", [])

        # 移除已存在的同名条目
        recent = [r for r in recent if r.get("path") != project_path]

        # 在头部插入新条目
        recent.insert(0, {"path": project_path, "name": project_name})

        # 限制数量
        max_count = cls.get("max_recent_projects", 10)
        cls.set("recent_projects", recent[:max_count])
        cls.save()

    @classmethod
    def get_recent_projects(cls) -> List[Dict[str, str]]:
        """获取最近打开的项目列表"""
        return cls.get("recent_projects", [])

    @classmethod
    def reset_to_defaults(cls):
        """重置所有设置为默认值"""
        cls._settings = dict(cls.DEFAULTS)
        cls.save()

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """获取所有设置（合并默认值）"""
        result = dict(cls.DEFAULTS)
        result.update(cls._settings)
        return result
