# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .version import VERSION

class Config:
    """全局配置管理类"""
    _config: Dict[str, Any] = {}
    _config_dir: Path = None
    
    @classmethod
    def load_config(cls, custom_config_path: Optional[str] = None):
        """加载配置文件"""
        # 确定配置目录
        if custom_config_path:
            config_path = Path(custom_config_path)
            cls._config_dir = config_path.parent
        else:
            # 默认配置目录
            cls._config_dir = Path(__file__).parent.parent.parent / "config"
            config_path = cls._config_dir / "app_config.json"
        
        # 加载主配置
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cls._config = json.load(f)
        else:
            # 默认配置
            cls._config = cls._get_default_config()
        
        # 加载数据库配置
        db_config_path = cls._config_dir / "database_config.json"
        if db_config_path.exists():
            with open(db_config_path, "r", encoding="utf-8") as f:
                cls._config["database"] = json.load(f)
        
        # 加载API配置
        api_config_path = cls._config_dir / "api_config.json"
        if api_config_path.exists():
            with open(api_config_path, "r", encoding="utf-8") as f:
                cls._config["api"] = json.load(f)
    
    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app_name": "Python项目管理工具",
            "version": VERSION,  # 从 version.py 动态读取版本号
            "default_project_path": "./Projects",
            "language": "zh-CN",
            "theme": "light",
            "auto_backup": True,
            "backup_interval": 3600,
            "api_enabled": True,
            "api_host": "127.0.0.1",
            "api_port": 5000,
            "debug_mode": False,
            "database": {
                "db_type": "sqlite",
                "db_path": "data/project_manager.db",
                "echo": False,
                "auto_migrate": True
            },
            "api": {
                "secret_key": "default-secret-key",
                "token_expire_hours": 24,
                "cors_enabled": True
            }
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """获取配置项"""
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
        """设置配置项"""
        keys = key.split(".")
        config = cls._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @classmethod
    def save(cls):
        """保存配置到文件"""
        if not cls._config_dir:
            raise RuntimeError("配置目录未初始化")
        
        # 保存主配置
        main_config = {k: v for k, v in cls._config.items() 
                      if k not in ["database", "api"]}
        with open(cls._config_dir / "app_config.json", "w", encoding="utf-8") as f:
            json.dump(main_config, f, indent=4, ensure_ascii=False)
        
        # 保存数据库配置
        if "database" in cls._config:
            with open(cls._config_dir / "database_config.json", "w", encoding="utf-8") as f:
                json.dump(cls._config["database"], f, indent=4, ensure_ascii=False)
        
        # 保存API配置
        if "api" in cls._config:
            with open(cls._config_dir / "api_config.json", "w", encoding="utf-8") as f:
                json.dump(cls._config["api"], f, indent=4, ensure_ascii=False)
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """获取配置目录"""
        return cls._config_dir
    
    @classmethod
    def get_data_dir(cls) -> Path:
        """获取数据存储目录"""
        data_dir = Path(__file__).parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir

    @classmethod
    def get_resolved_project_path(cls) -> str:
        import sys as _sys
        raw = cls.get("default_project_path", "./Projects")
        if not raw:
            raw = "./Projects"
        p = Path(raw)
        if p.is_absolute():
            if p.exists() and p.is_dir():
                try:
                    (p / ".write_test").touch()
                    (p / ".write_test").unlink()
                    return str(p)
                except Exception:
                    pass
            p = Path("./Projects")
        if getattr(_sys, 'frozen', False):
            base = Path(_sys.executable).parent
        else:
            base = Path.cwd()
        resolved = (base / p).resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        return str(resolved)
