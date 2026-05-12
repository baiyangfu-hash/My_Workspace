# Checklist: 交付物打包系统性修复

## Task 1: build_delivery.py 脚本
- [ ] 脚本文件存在于 `scripts/build_delivery.py`
- [ ] `--version` 参数正确解析
- [ ] `--skip-build` 参数跳过编译步骤
- [ ] `--verify-only` 参数仅验证已有zip
- [ ] Step 1 编译检查: 检测dist/exe存在且>50MB
- [ ] Step 2 文件复制: exe + _internal + config(4) + db + docs 全部复制成功
- [ ] Step 3 目录校验: 6项检查全部通过
- [ ] Step 4 打包: 使用zipfile.ZIP_DEFLATED (非PowerShell)
- [ ] Step 5 ZIP校验: CHK-001~007 全部PASS
- [ ] Step 6 报告: 输出格式正确含Final Status

## Task 2: 全局规范修复 (V2.1.0 → V2.2.0)
- [ ] D1修复: L526不再出现"Compress-Archive"
- [ ] D2修复: L438-467目录结构对齐项目实际
- [ ] D3修复: L897 ZIP正常范围改为150-170MB
- [ ] D4修复: 附录A包含build_delivery.py源码
- [ ] 版本号更新为V2.2.0
- [ ] 变更记录表新增V2.2.0条目

## Task 3: V2.4.3 验证
- [ ] 脚本执行无报错
- [ ] 报告显示 🟢 RELEASE APPROVED
- [ ] 新生成zip文件数=951 (±5)
- [ ] 新生成zip大小≈160MB (±5MB)
- [ ] zip内含01_可执行文件/目录

## Task 4: 清理
- [ ] 项目根目录无 `_*.py` 临时脚本残留
- [ ] 06_交付物/根目录无多余散落文件
