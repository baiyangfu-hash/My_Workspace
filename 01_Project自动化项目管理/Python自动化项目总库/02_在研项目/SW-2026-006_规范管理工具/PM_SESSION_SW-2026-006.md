# PM_SESSION_SW-2026-006

## 0. Meta
- project_id: SW-2026-006
- project_name: 规范管理工具 (SpecMgr)
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-006_规范管理工具
- last_updated: 2026-05-26
- owners: fubai

## 1. Positioning（项目定位）
- one_liner: 规范管理体系的一站式管理工具（CLI + GUI），支持桌面操作和免安装exe分发
- users: 个人开发者/AI助手/其他工作人员（通过GUI降低使用门槛）
- non_goals: 不做Obsidian插件、不做Web界面(B/S架构)、不做规范内容编辑器、不做多用户并发/权限管理

## 2. Current Focus（当前焦点）
- current_focus: V0.2.0已验证可用，CLI在真实workspace上4个命令全部正常运行，已注册到全局规范仓库
- milestone: V0.2.0 完成 ✅（真实workspace验证通过）
- acceptance: CLI 4命令(check/index/frontmatter/report)在真实workspace上运行正常，SW-2026-006已注册到spec_registry.json

## 3. Status Summary（当前状态摘要）
- in_progress:
  - V0.2.0真实workspace验证通过（check/index/frontmatter/report全部正常）
  - SW-2026-006已注册到全局spec_registry.json（cross-domain域）
  - 新增__main__.py支持python -m specmgr调用
- next_up:
  - V0.3.0 GUI MVP（PySide6基本框架+仪表盘+检查页）
  - V0.4.0 GUI完善（索引/Frontmatter/报告/设置页）
  - V0.5.0 打包分发（PyInstaller打包exe）
- open_questions:
  - PySide6打包后体积是否可控制在100MB以内？
  - GUI是否需要国际化(i18n)支持？
- risks_dependencies:
  - PySide6依赖体积较大，打包后可能超过100MB
  - 依赖spec_registry.json的数据格式稳定性
  - HealthChecker.run_all()中8个Checker独立调用scan_all()，存在重复扫描性能瓶颈（建议V0.3.0优化）

## 4. Artifacts Index（文档索引）
- prd:
  - 01_需求与设计/01-产品需求文档_PRD-V1.1.0.md
- req:
  - (待创建)
- des:
  - 01_需求与设计/02-技术方案文档_DES-V1.1.0.md
- test:
  - 01_需求与设计/03-测试报告_V0.2.0.md
  - 02_源代码/tests/conftest.py
  - 02_源代码/tests/test_registry.py
  - 02_源代码/tests/test_scanner.py
  - 02_源代码/tests/test_checker_base.py
  - 02_源代码/tests/test_services.py
  - 02_源代码/tests/test_cli.py
- change_mgmt:
  - (无)
- delivery:
  - (无)

## 5. Logs（按事件沉淀）
- change_log:
  - 2026-05-24 项目立项，从规范管理体系根治方案中拆分出工具项目
  - 2026-05-25 需求变更：新增GUI(PySide6)和打包(exe)需求，产品定位从"CLI工具"扩展为"CLI+GUI管理工具" 影响范围:PRD/DES/架构/里程碑 状态:已批准
  - 2026-05-25 审查发现：PRD/DES磁盘文件名为V1.0.0，但PM_SESSION索引曾指向V1.1.0，已修正为实际文件名
  - 2026-05-25 文档版本重命名：PRD/DES文件名从V1.0.0重命名为V1.1.0，与内容一致
  - 2026-05-25 SW-2026-006注册到全局spec_registry.json（cross-domain域），CLI在真实workspace验证通过
  - 2026-05-26 需求确认：SpecMgr已支持全域规范管理（PM/PLC/Python），在全局规则project-rule.md中新增SpecMgr CLI使用说明，明确AI助手和开发者应通过CLI管理规范 影响范围:全局规则文档 状态:已完成
- iteration_log:
  - 2026-05-24 迭代V0.1.0启动，目标: MVP四命令可用
  - 2026-05-25 里程碑调整: V0.1.0(CLI MVP)→V0.2.0(Service重构)→V0.3.0(GUI MVP)→V0.4.0(GUI完善)→V0.5.0(打包)→V1.0.0(正式)
  - 2026-05-25 V0.2.0 Service层重构代码完成 状态:代码完成
  - 2026-05-25 V0.2.0审查问题修复+单元测试完成：77项测试全部通过 状态:完成 ✅
- bug_log:
  - 2026-05-25 find_duplicates()跳过不同文件名的同ID副本 P1 已修复
  - 2026-05-25 VersionMismatchChecker版本比较未规范化V前缀 P1 已修复
  - 2026-05-25 RulesPathChecker/DeprecatedRefChecker的findall正则使用捕获组导致只返回前缀 P1 已修复
  - 2026-05-25 scanner正则不支持CODE/LSP/INT等短格式spec ID P1 已修复
  - 2026-05-25 registry.save()不持久化API修改的数据 P1 已修复
  - 2026-05-25 Frontmatter生成使用字符串拼接而非yaml.dump() P1 已修复
  - 2026-05-25 CLI子命令workspace参数冗余 P2 已修复
  - 2026-05-25 Service层不检查注册表加载结果 P2 已修复
  - 2026-05-25 pyproject.toml build-backend非标准值 P2 已修复
  - 2026-05-25 config.py DEFAULT_OUTPUT_PATHS路径与DES不一致 P2 已修复
- refactor_log:
  - 2026-05-25 V0.2.0 Service层重构：从commands提取业务逻辑到services，Commands改为薄壳 状态:代码完成
  - 2026-05-25 检查器与PRD对齐：SHC-004检查文件存在性、SHC-006检查链接目标存在性、SHC-007改为INFO、SHC-008路径无效改为ERROR 状态:完成
  - 2026-05-25 CLI参数统一：workspace通过ctx.obj传递，子命令不再重复定义 状态:完成
  - 2026-05-25 spec ID正则统一：扩展支持CODE/LSP/INT前缀和短格式 状态:完成
- release_log:
  - 2026-05-25 V0.2.0 范围:Service层重构+审查问题修复+77项单元测试 状态:完成 ✅
