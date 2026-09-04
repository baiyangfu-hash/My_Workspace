"""Wrapper: 迁移插件字段脚本

此脚本位于项目根 `scripts/`，作为集中化入口，内部调用核心代码目录下的实现。
用法:
    python migrate_plugin_fields.py [path/to/project_manager.db]
"""
import sys
from pathlib import Path

def main(argv=None):
    argv = argv or sys.argv[1:]
    db_path = argv[0] if argv else None

    # 导入核心实现并调用
    from src.scripts.migrate_plugin_fields import run_migration

    success = run_migration(db_path)
    return 0 if success else 1

if __name__ == '__main__':
    raise SystemExit(main())
