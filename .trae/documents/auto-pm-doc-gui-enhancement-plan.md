# auto-pm (SW-2026-008) 文档补充 + GUI对齐计划 (V2)

## Summary

为 auto-pm 项目补充缺失的技术文档（INT/DSN/TEC）、修订PRD、更新README、创建CHANGELOG、更新PM_SESSION，并将GUI对齐原型设计。

## 执行策略调整 (V2)

**原方案问题**: 3个大文档并行用subagent创建，结果全部丢失
**新策略**: 分3阶段顺序执行，文档直接在主对话创建，避免subagent失败

## 阶段划分

### 阶段1: 快速文档更新（3个任务，简单编辑）
- Task 1: 修订PRD ✅ 已完成
- Task 5: 重写README.md
- Task 6: 创建CHANGELOG.md
- Task 7: 更新PM_SESSION

### 阶段2: 核心设计文档（3个任务，直接创建）
- Task 2: 创建INT接口文档
- Task 3: 创建DSN详细设计说明书
- Task 4: 创建TEC技术方案文档

### 阶段3: GUI对齐原型（2个任务，代码修改）
- Task 8: GUI后端API扩展
- Task 9: GUI前端扩展

## Current State Analysis

### 已有文档
| 文档 | 状态 | 问题 |
|------|------|------|
| `00_项目基础信息/001_产品需求文档_PRD.md` | ✅ 已修订 | frontmatter/信息表/变更记录已补充 |
| `PM_SESSION_SW-2026-008.md` | P5状态过时 | 仍标注"P5规划中"，实际P5已全部实现 |
| `README.md` | 严重过时 | 仍是脚手架模板默认内容 |
| `CHANGELOG.md` | 不存在 | pyproject.toml引用了但文件不存在 |

### 缺失文档
| 文档 | 前缀码 | 说明 |
|------|--------|------|
| 接口文档 | INT | CLI + Service + JS Bridge API |
| 详细设计说明书 | DSN | 数据库/状态机/模板/GUI设计 |
| 技术方案文档 | TEC | 技术选型/增量扫描/数据真源 |

### GUI差距
| 功能 | 原型 | 实际GUI | 差距 |
|------|------|---------|------|
| 概览Tab | 有（含变更概览+最近活动） | 有（仅基本信息） | 缺变更概览统计和最近活动 |
| 变更单Tab | 有（含新建按钮） | 有（仅查看） | 缺新建变更单功能 |
| 文档Tab | 有 | 无 | 完全缺失 |
| 规范检查Tab | 有 | 无 | 完全缺失 |
| 阶段筛选 | 有 | 无 | 缺失 |

## Proposed Changes

### Task 1: 修订PRD文档 ✅ 已完成
**文件**: `00_项目基础信息/001_产品需求文档_PRD.md`
**操作**: 添加YAML frontmatter、文档基础信息表、版本变更记录表

### Task 5: 重写README.md
**文件**: `README.md`
**操作**: 完全重写，内容包括:
- 项目简介（一句话定位）
- 功能特性（6大命令组概览）
- 安装（pip install / 开发模式）
- CLI使用（所有命令+示例）
- GUI使用（启动方式、功能说明）
- 开发指南（测试/lint/类型检查命令）
- 项目结构
- 技术栈列表

### Task 6: 创建CHANGELOG.md
**文件**: `CHANGELOG.md`
**格式**: Keep a Changelog格式
**内容**: 基于PM_SESSION的实施日志，整理P1-P5的变更记录

### Task 7: 更新PM_SESSION
**文件**: `PM_SESSION_SW-2026-008.md`
**操作**:
- 更新§2 Current Focus: P5已完成
- 更新§3 Status Summary: P5标记为completed
- 更新§4 Artifacts Index: 补充int/dsn/tec文档路径
- 更新§5 Logs: 补充P5完成记录
- 更新§8 Handoff Notes: 反映当前实际状态
- 更新§9 Next Actions: 更新为文档补充+GUI增强

### Task 2: 创建接口文档(INT)
**文件**: `00_项目基础信息/002_接口文档_INT.md`
**规范依据**: INT-215 Python接口文档模板
**内容覆盖三部分**:
- Part A: CLI命令接口（6组命令）- 参数表、输出格式、退出码、示例
- Part B: Service层Python API - 签名、参数、返回类型、异常
- Part C: GUI JS Bridge API - 参数、ApiResponse[T]格式、成功/失败响应示例

### Task 3: 创建详细设计说明书(DSN)
**文件**: `00_项目基础信息/003_详细设计说明书_DSN.md`
**内容**:
1. 设计概述（设计目标、设计原则）
2. 系统架构（分层架构图、模块依赖关系）
3. 数据库设计（3表DDL、索引、关系图）
4. 状态机设计（变更管理状态机、门禁规则）
5. Copier模板设计（plc-standard/python-tool结构、问题定义、渲染规则）
6. GUI原型设计（布局说明、Tab功能、交互流程）
7. 路径安全设计（path_resolver防遍历攻击策略）
8. 变更记录

### Task 4: 创建技术方案文档(TEC)
**文件**: `00_项目基础信息/004_技术方案文档_TEC.md`
**内容**:
1. 技术方案概述（项目背景、技术选型论证）
2. 技术选型（Click vs Typer、Pydantic vs dataclass、SQLite vs JSON、pywebview vs PySide6、Copier vs Cookiecutter）
3. 增量扫描策略（file_mtime判据、扫描流程、缓存一致性保证）
4. 数据真源策略（三源并存设计、同步规则、冲突处理）
5. CLI插件架构（Click子命令组、延迟导入、技术栈扩展点）
6. GUI技术方案（pywebview JS Bridge模式、ApiResponse统一格式、前后端通信）
7. 变更记录

### Task 8: GUI对齐原型 - 后端API扩展
**文件**: `auto_pm/gui/api.py`
**操作**:
- 新增 `run_check(project_id)` 方法 - 调用PlcChecker
- 新增 `repair_project(project_id, rename)` 方法 - 调用PlcRepairer
- 新增 `create_change(project_id, domain, nature, scope, applicant, background, necessity, ...)` 方法 - 调用ChangeService
- 新增 `list_project_docs(project_id)` 方法 - 扫描项目文档状态
- 新增 `standardize_project(project_id, apply)` 方法 - 调用plc standardize
- 修改 `get_project(project_id)` - 增加变更概览统计和最近活动

### Task 9: GUI对齐原型 - 前端扩展
**文件**: `auto_pm/gui/static/index.html`, `auto_pm/gui/static/app.js`, `auto_pm/gui/static/style.css`
**操作**:
- 添加"文档"Tab（文档状态表格 + 创建/查看操作）
- 添加"规范检查"Tab（检查结果表格 + 运行检查/自动修复按钮）
- 概览Tab增加变更概览统计和最近活动
- 变更单Tab增加新建变更单弹窗
- 工具栏增加阶段筛选下拉框
- 添加新建变更单弹窗表单

## Assumptions & Decisions

1. **文档格式**: INT遵循INT-215模板；DSN/TEC适配Python项目特点
2. **文档命名**: 遵循DEV-004前缀码体系
3. **PRD修订**: 仅补充格式要素，不改变内容 ✅
4. **GUI增强范围**: 仅对齐原型已有功能
5. **python子命令**: 保持占位状态
6. **执行策略**: 分阶段顺序执行，文档直接创建

## Verification Steps

1. 所有新建/修改的文档文件存在且内容完整
2. PRD添加了frontmatter和文档基础信息表 ✅
3. INT文档覆盖CLI/Service/JS Bridge三部分接口
4. DSN文档包含数据库设计、状态机设计、模板设计
5. TEC文档包含技术选型论证和架构决策
6. README反映实际CLI命令和功能
7. CHANGELOG格式符合Keep a Changelog
8. PM_SESSION反映P5完成状态
9. GUI新增文档Tab和规范检查Tab可用
10. GUI新建变更单功能可用
11. `ruff check` + `mypy` 通过
12. 现有测试不回归
