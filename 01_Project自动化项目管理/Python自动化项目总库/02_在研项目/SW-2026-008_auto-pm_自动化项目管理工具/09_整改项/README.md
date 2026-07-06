# 09_整改项 索引

> **项目**: SW-2026-008 auto-pm 自动化项目管理工具
> **维护规则**: 历史整改文件归档到 `archive/` 子目录；当前活跃整改文件保留在根目录
> **最近整理**: 2026-07-07（V0.9.0 重新诊断 + 整改项目录归档）

## 当前活跃文件（2 个）

| 文件 | 用途 | 状态 |
|------|------|------|
| [diagnostic_report.md](diagnostic_report.md) | 2026-07-07 重新诊断报告（V0.9.0 实测 ruff 26 errors + mypy 34 errors + pytest 阻断 + 15 项新发现问题） | ✅ 当前真源 |
| [README.md](README.md) | 09_整改项索引（本文件） | ✅ 当前真源 |

## 归档文件（archive/，15 个）

### 2026-07-07 重新诊断时归档（5 个）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/diagnostic_report_2026-07-06_V0.9.0.md](archive/diagnostic_report_2026-07-06_V0.9.0.md) | 2026-07-06 | 被 2026-07-07 重新诊断报告替代（旧报告声明 ruff/mypy 0 errors 与实测不符） |
| [archive/2026-06-30_项目全量审查报告.md](archive/2026-06-30_项目全量审查报告.md) | V0.4.1 | 审查的是 V2.1 设计文档（已迁移到 02_设计/），9 Critical/20 Major 问题大多已修复 |
| [archive/GUI-UI对比度问题清单.md](archive/GUI-UI对比度问题清单.md) | V0.5.x | 基于 QWidget 截图，引用 `scripts/gui_plc_full_test.py`（V0.9.0 已删除） |
| [archive/GUI测试整改报告.md](archive/GUI测试整改报告.md) | V0.5.0 | 自标 "已过时"，引用 `02_设计/GUI测试计划-V0.5.0.md`（不存在）等已删除文件 |
| [archive/V0.4.2-glm执行输入清单.md](archive/V0.4.2-glm执行输入清单.md) | V0.4.2 | 引用 `00_项目基础信息/005_变更记录_CHG.md`（已归档不存在），主线已到 V0.9.0 |

### V0.5.0 收口时归档（7 个，2026-07-01）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/GUI-V2.0-测试执行报告.md](archive/GUI-V2.0-测试执行报告.md) | V2.0 GUI 测试 | V2.0 GUI 已被 V2.2/V2.3 GUI 改造取代 |
| [archive/V0.2.1-电气工程师评估整改清单.md](archive/V0.2.1-电气工程师评估整改清单.md) | V0.2.1 | 评估项已在 V0.3.0+ 全部落地 |
| [archive/V0.3.0-项目深度诊断与Dogfood专项报告.md](archive/V0.3.0-项目深度诊断与Dogfood专项报告.md) | V0.3.0 | Dogfood 已 25 次闭环，诊断结论已沉淀 |
| [archive/V0.3.0-项目落地执行总计划_重规划版.md](archive/V0.3.0-项目落地执行总计划_重规划版.md) | V0.3.0 | 计划已被 V0.5.0+ 长期路线图取代 |
| [archive/V0.3.6-glm5.1执行输入清单.md](archive/V0.3.6-glm5.1执行输入清单.md) | V0.3.6 | 执行清单已全部完成 |
| [archive/V0.4.0-Codex_GPT产品与工程建议.md](archive/V0.4.0-Codex_GPT产品与工程建议.md) | V0.4.0 | 建议已在 V0.4.0~V0.5.0 评估落地 |
| [archive/V0.4.0-glm5.2执行输入清单.md](archive/V0.4.0-glm5.2执行输入清单.md) | V0.4.0 | 执行清单已全部完成 |

### V0.4.2 收口时归档（2 个，2026-06-29）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/V2.0-GUI-验证整改清单.md](archive/V2.0-GUI-验证整改清单.md) | V2.0 | V2.0 GUI 验证已完成 |
| [archive/V2.0-测试执行检查清单.md](archive/V2.0-测试执行检查清单.md) | V2.0 | V2.0 测试执行已完成 |

### V0.4.0 收口时归档（1 个，2026-06-28）

| 文件 | 原活跃期 | 归档原因 |
|------|----------|----------|
| [archive/V2.0-全功能自动化测试计划.md](archive/V2.0-全功能自动化测试计划.md) | V2.0 | V2.0 全功能测试计划已执行完毕 |

### 迭代测试报告（archive/iterations/，4 个）

| 文件 | 用途 |
|------|------|
| [archive/iterations/迭代1-测试报告.md](archive/iterations/迭代1-测试报告.md) | M1 迭代 1 测试报告 |
| [archive/iterations/迭代2-测试报告.md](archive/iterations/迭代2-测试报告.md) | M1 迭代 2 测试报告 |
| [archive/iterations/迭代3-测试报告.md](archive/iterations/迭代3-测试报告.md) | M1 迭代 3 测试报告 |
| [archive/iterations/迭代4-测试报告.md](archive/iterations/迭代4-测试报告.md) | M1 迭代 4 测试报告 |

## 整理规则

1. **归档时机**：每个版本收口时（如 V0.5.0/V0.6.0/V0.9.0），将已完成的历史整改文件移动到 `archive/`
2. **保留原则**：当前活跃的诊断报告和执行清单保留在根目录，便于快速访问
3. **索引维护**：每次归档操作后更新本 README 索引
4. **历史追溯**：归档文件不删除，保留完整历史链路
5. **命名规范**：归档文件保留原名，不追加版本号后缀（例外：`diagnostic_report_2026-07-06_V0.9.0.md` 因同名文件需区分，添加日期前缀）

## 2026-07-07 重新诊断关键发现摘要

> ⚠️ **PM_SESSION §3 spec_compliance 声明失真**：声称 "ruff 0 + mypy 0 + 999 passed"，实测为 "ruff 26 errors + mypy 34 errors + pytest INTERNALERROR"。

**P0 阻断性问题（7 项）**：
1. `protocols.py` 断裂导入（ImportError: cannot import name 'ProjectCardDTO'）
2. `workbench_bridge.py` 方法名不匹配（get_dashboard_summary vs get_dashboard_snapshot）
3. `tests/qml/test_qml_bridge_v08.py` 导入已删除的 qml_bridge.py
4. `project_service.py` 重复定义（get_last_sync_time / is_cache_available）
5. `project_service.py` 用旧字段构造新 ProjectCardDTO
6. PySide6 DLL 加载失败（pytest 完全无法启动）
7. `clean_bridge.py` 项目根目录临时文件

**已修复（对比 2026-07-06 旧报告）**：
- A1: QmlBridge 上帝类已拆分为 5 个 Domain Bridge ✅
- U1/U2/U3/D1/D2/D3/D4: README/归档索引/文档存放位置已修正 ✅

**部分修复（6 项）**：A2/A3/A4/C1/C2/C4/T1
**未修复（3 项）**：C3/C5/U5

详见 [diagnostic_report.md](diagnostic_report.md)。
