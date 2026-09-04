Scripts directory: centralized entry points and QA runner

- `build.py`, `package.py`, `migrate_plugin_fields.py`, `build_delivery.py`: entry scripts for build/delivery tasks.
- `migrate_plugin_fields.py` and `build_delivery.py` in this folder are thin wrappers that call implementations under `03_主程序/01_主程序核心代码/src/scripts/`.
- `qa/run_all_tests.py`: runs legacy test scripts found in `06_交付物/03_测试文件` sequentially.

Usage examples:
    python migrate_plugin_fields.py [path/to/project_manager.db]
    python build_delivery.py --version V2.6.0
    python qa/run_all_tests.py

Note: 原始实现文件保留在 `03_主程序/01_主程序核心代码/scripts/`，便于维护源码与打包一致性。
