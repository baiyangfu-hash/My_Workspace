---
alwaysApply: true
scene: git_message
description: Git提交信息规范，定义类型、scope、格式和示例
---

# Git 提交信息规范

## 格式模板

```
<type>(<scope>): <描述>

[可选body: 详细说明变更原因/影响]

[可选footer: 关联变更单/Breaking Change]
```

**一行式**（无body/footer时）：
```
<type>(<scope>): <描述>
```

## 允许的类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新增功能/逻辑/功能块 | `feat(SysLib): 新增FB_TONR累加定时器功能块` |
| `fix` | 修复bug、逻辑错误、参数错误 | `fix(OB1): 修复主循环中定时器未初始化的问题` |
| `docs` | 更新文档、说明、报警码定义 | `docs(905规范): 更新SCL编程规范的命名章节` |
| `refactor` | 重构代码结构、优化逻辑、整理变量 | `refactor(CheckService): 提取公共检查逻辑到基类` |
| `chore` | 配置文件、版本号、依赖等非代码变更 | `chore(pyproject): 升级PySide6依赖至6.7` |
| `test` | 新增/修改测试逻辑、仿真脚本 | `test(FB_TON): 新增定时器边界条件测试用例` |

## Scope（范围）规则

Scope标注变更影响的模块/项目，**必须使用项目中实际的模块名**：

### PLC域常用scope

| scope | 说明 |
|-------|------|
| `SysLib` | 共享函数库 |
| `OB1` | 主程序 |
| `FB_xxx` | 具体功能块（如 `FB_ValveControl`） |
| `DB1` | 全局变量数据块 |
| `conveyor` | 输送机模块 |
| `pickplace` | 取放料机构 |
| `feeder` | 打胶机送料 |

### Python域常用scope

| scope | 说明 |
|-------|------|
| `ProjectService` | 项目管理服务 |
| `CheckService` | 规范检查服务 |
| `SpecRegistry` | 规范注册表 |
| `SpecScanner` | 规范扫描器 |
| `IndexService` | 索引生成服务 |
| `pyproject` | 项目配置 |
| `constants` | 常量定义 |

### 规范/配置域常用scope

| scope | 说明 |
|-------|------|
| `spec_registry` | 规范注册表数据 |
| `project-rule` | 全局开发规则 |
| `plc-rules` | PLC技术栈规则 |
| `python-rules` | Python技术栈规则 |
| `gitignore` | Git忽略规则 |

## 描述要求

- 必须用**中文**，清晰说明变更内容，控制在50字以内
- 禁止模糊描述，如"修改了代码""优化了逻辑"等
- 描述必须与变更内容相关，不能与项目无关
- 使用祈使句风格（"新增"而非"新增了"，"修复"而非"修复了"）

## 关联变更单

当提交关联变更管理流程时，在footer中标注：

```
fix(FB_ValveControl): 修复阀门控制时序错误

Ref: CHG-DOCU-2026-001
```

## Breaking Change标记

当变更破坏向后兼容性时，在footer中标注：

```
feat(SpecRegistry): 重构注册表数据结构

BREAKING CHANGE: spec_id字段从数字改为字符串，旧版注册表需迁移
```

## 完整示例

### PLC域

```
feat(SysLib): 新增FB_TONR累加定时器功能块
```

```
fix(FB_ValveControl): 修复阀门开启延时未生效的问题
```

```
refactor(conveyor): 将输送机状态机从OB1提取到独立FB
```

### Python域

```
feat(CheckService): 新增规范版本漂移检测检查器
```

```
fix(SpecRegistry): 修复save方法不持久化API修改的数据
```

```
test(SpecScanner): 新增spec ID正则匹配的边界测试
```

### 规范/配置域

```
docs(905规范): 更新SCL编程规范的METHOD章节说明
```

```
chore(spec_registry): 注册DEV-301别名兼容映射
```

```
docs(project-rule): 新增auto-pm工具说明和安全红线规则
```
