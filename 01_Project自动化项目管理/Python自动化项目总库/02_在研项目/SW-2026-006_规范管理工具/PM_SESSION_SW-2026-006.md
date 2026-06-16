# PM_SESSION_SW-2026-006

## 0. Meta
- project_id: SW-2026-006
- project_name: 规范管理工具 (SpecMgr)
- project_root: c:\Users\fubai\Desktop\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\02_在研项目\SW-2026-006_规范管理工具
- last_updated: 2026-06-16
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
  - 01_需求与设计/01-产品需求文档_PRD.md
- req:
  - (待创建)
- des:
  - 01_需求与设计/02-技术方案文档_DES.md
- test:
  - 01_需求与设计/03-测试报告_V0.2.0.md
  - 02_源代码/tests/conftest.py
  - 02_源代码/tests/test_registry.py
  - 02_源代码/tests/test_scanner.py
  - 02_源代码/tests/test_checker_base.py
  - 02_源代码/tests/test_services.py
  - 02_源代码/tests/test_cli.py
- user_guide:
  - 01_需求与设计/04-使用手册_UG.md
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
  - 2026-05-28 新增使用手册：创建04-使用手册_UG-V0.2.0.md，涵盖CLI完整使用指南和GUI设计预览 影响范围:文档 状态:已完成
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

## Spec Snapshot（初始化时锁定，供后续版本漂移检测）

> 以下版本号在项目初始化时从 `spec_registry.json` 读取并填入。
> 本区块作为基线，后续 `specmgr check` 对比当前规范版本与快照，检测版本漂移。

| spec_id | 版本 | 记录日期 | 说明 |
|---------|------|---------|------|
| PROJ-016 | V1.0.0 | 2026-06-06 | 通用项目结构模板 |
| PRD-001 | V1.0.0 | 2026-06-06 | 产品需求文档模板 |
| DEV-031 | V1.0.0 | 2026-06-06 | 通用测试规范 |
| DEV-032 | V1.0.0 | 2026-06-06 | GUI测试方案标准 |
| DEV-210 | V1.1.0 | 2026-06-06 | Python编程规范 |
| DEV-211 | V1.0.0 | 2026-06-06 | Python代码审查规范 |
| DEV-220 | V2.2.0 | 2026-06-06 | Python项目打包规范 |
| INT-215 | V1.0.0 | 2026-06-06 | Python接口文档模板 |
| DEV-004 | V1.1.1 | 2026-06-06 | 通用项目文档版本管理与变更核心规范 |
| CHG-040 | V2.0.0 | 2026-06-06 | 通用变更单模板 |
| CHG-041 | V2.1.0 | 2026-06-06 | 通用版本变更台帐模板 |
| PM-042 | V2.1.0 | 2026-06-06 | 通用变更管理流程规范 |

## 6. Implementation Log
- 2026-05-25 | skill=fullstack-engineer | mode=全栈开发
  - goal: V0.2.0 Service层重构 + 审查问题修复 + 77项单元测试
  - changed_files: specmgr/下全部文件
  - impact: CLI 4命令(check/index/frontmatter/report)在真实workspace验证通过
  - risks: HealthChecker.run_all()中8个Checker独立调用scan_all()存在性能瓶颈

## 7. Verification Log
- 2026-05-25
  - verified: 77项单元测试全部通过, CLI 4命令在真实workspace运行正常
  - not_verified: GUI(PySide6)功能, PyInstaller打包
  - method: pytest + CLI手动验证
  - blocker: 无

## 8. Handoff Notes
- 2026-05-28 | from=pm-workflow
  - current_state: V0.2.0已验证可用，已注册到全局规范仓库
  - next_focus: V0.3.0 GUI MVP（PySide6基本框架+仪表盘+检查页）
  - watchouts: PySide6打包后体积可能超过100MB; HealthChecker性能瓶颈待优化
  - read_first: PM_SESSION_SW-2026-006.md, 01_需求与设计/04-使用手册_UG.md

## 9. Next Actions
- [P1] V0.3.0 GUI MVP | precondition=PySide6环境就绪 | done_when=基本框架+仪表盘+检查页可用
- [P2] HealthChecker性能优化 | precondition=无 | done_when=run_all()不再重复扫描
- [P3] V0.5.0 PyInstaller打包 | precondition=GUI MVP完成 | done_when=exe可独立运行
- [P4] 4.2 SpecMgr索引服务增强（废弃规范展示） | source=SYS-2026-001 Phase 4 | priority=中 | done_when=索引输出包含废弃规范标记
- [P4] 4.3 SpecMgr diagnose子命令 | source=SYS-2026-001 Phase 4 | priority=低 | done_when=diagnose子命令可用
- [P4] 4.4 SpecMgr fix子命令 | source=SYS-2026-001 Phase 4 | priority=低 | done_when=fix子命令可用
- [P4] 4.6 规范元数据汇总报告重新生成 | source=SYS-2026-001 Phase 4 | priority=中 | done_when=报告与当前spec_registry一致
- [P4] 4.7 索引文件重新生成 | source=SYS-2026-001 Phase 4 | priority=中 | done_when=索引文件与当前规范目录一致
- [P4] 4.8 SpecMgr check验证 | source=SYS-2026-001 Phase 4 | priority=中 | done_when=check命令在workspace上通过
