# Tasks: 交付物打包系统性修复

## Task 1: 创建 build_delivery.py 统一构建脚本
- [ ] 1.1 创建文件 `scripts/build_delivery.py`
- [ ] 1.2 实现命令行参数解析 (--version, --skip-build, --verify-only)
- [ ] 1.3 实现 Step 1: 编译检查 (PyInstaller)
- [ ] 1.4 实现 Step 2: 更新06_交付物/ (exe+config+db+docs映射复制)
- [ ] 1.5 实现 Step 3: 交付物目录校验 (6项检查)
- [ ] 1.6 实现 Step 4: 打包zip (Python zipfile.ZIP_DEFLATED, 禁止PowerShell)
- [ ] 1.7 实现 Step 5: ZIP校验 (7项CHK + 阈值)
- [ ] 1.8 实现 Step 6: 输出报告 (彩色终端格式)

## Task 2: 修复全局规范 220_V2.1.0 → V2.2.0
- [ ] 2.1 修改D1: L526 "Compress-Archive或7z" → "Python zipfile"
- [ ] 2.2 修改D2: L438-467 目录结构从8目录改为实际6目录
- [ ] 2.3 修改D3: L897 ZIP阈值 100-110MB → 150-170MB
- [ ] 2.4 修改D4: 新增附录A (build_delivery.py完整源码)
- [ ] 2.5 更新版本号 V2.1.0 → V2.2.0
- [ ] 2.6 更新变更记录表

## Task 3: 用新脚本验证V2.4.3
- [ ] 3.1 运行 `python build_delivery.py --version V2.4.3 --skip-build`
- [ ] 3.2 检查输出报告全部PASS
- [ ] 3.3 对比新生成zip与现有V2.4.3 zip一致

## Task 4: 清理残留临时文件
- [ ] 4.1 删除 `_diagnose_templates.py`
- [ ] 4.2 删除 `_list_tables.py`
- [ ] 4.3 删除 `_self_test_01_db_diagnose.py`
- [ ] 4.4 删除 `_self_test_02_init_test.py`
- [ ] 4.5 删除 `_self_test_03_create_projects.py`
- [ ] 4.6 检查并清理06_交付物根目录散落文件
