# -*- coding: utf-8 -*-
"""
默认项目结构模板数据

V2.8.0: 内置模板数据已迁移到 config/templates/*.yaml
本文件保留 DEFAULT_TEMPLATES 作为向后兼容的懒加载代理。
现有 `from src.core.constants import DEFAULT_TEMPLATES` 无需修改。
"""
import os
from pathlib import Path
from typing import Any


def _load_builtin_templates_from_yaml() -> list[dict[str, Any]]:
    """从 config/templates/ 目录加载所有内置模板 YAML 文件"""
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML 未安装，请运行: pip install pyyaml")

    template_dir = Path(__file__).parent.parent.parent / "config" / "templates"
    if not template_dir.exists():
        raise FileNotFoundError(f"模板数据目录不存在: {template_dir}")

    templates = []
    for yaml_file in sorted(template_dir.glob("TPL-*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict):
                data["_source_file"] = yaml_file.name
                templates.append(data)

    return templates


class _DefaultTemplatesProxy(list):
    """DEFAULT_TEMPLATES 懒加载代理

    首次访问时从 YAML 文件加载，之后缓存结果。
    行为与普通 list 完全一致，支持索引、迭代、len 等操作。
    """

    def __init__(self):
        super().__init__()
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            data = _load_builtin_templates_from_yaml()
            # 用 extend 将数据填充到自身（list 子类）
            super().clear()
            super().extend(data)
            self._loaded = True

    def __getitem__(self, index):
        self._ensure_loaded()
        return super().__getitem__(index)

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()

    def __bool__(self):
        self._ensure_loaded()
        return super().__bool__()

    def __repr__(self):
        self._ensure_loaded()
        return super().__repr__()

    def __contains__(self, item):
        self._ensure_loaded()
        return super().__contains__(item)


# 向后兼容：DEFAULT_TEMPLATES 仍可正常使用
DEFAULT_TEMPLATES = _DefaultTemplatesProxy()
