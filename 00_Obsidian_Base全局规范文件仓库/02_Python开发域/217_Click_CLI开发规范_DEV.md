---
spec_id: "DEV-217"
title: "Click CLI 开发规范"
version: "V1.0.0"
domain: python
lifecycle: "active"
canonical_path: "00_Obsidian_Base全局规范文件仓库/02_Python开发域/217_Click_CLI开发规范_DEV.md"
tags: ["Click", "CLI", "开发规范"]
created: "2026-06-21"
updated: "2026-06-21"
---

# Click CLI 开发规范

## 文档基础信息

| 项目 | 内容 |
|------|------|
| 文档名称 | Click CLI 开发规范 |
| 文档类型 | DEV |
| 规范编号 | DEV-217 |
| 版本号 | V1.0.0 |
| 创建日期 | 2026-06-21 |
| 状态 | 已批准 |
| 适用范围 | 使用 Click 开发命令行工具的 Python 项目 |

## 变更记录

| 日期 | 版本 | 变更类型 | 变更内容 | 变更人员 |
|------|------|---------|---------|---------|
| 2026-06-21 | V1.0.0 | 新增 | 初始版本 | auto-pm |

## 1. 概述

本规范定义使用 Click 开发命令行工具的编码标准，基于 auto-pm V2.0 实践总结。

## 2. 项目结构

- CLI 入口放在 `cli/__main__.py`
- 命令组按功能域划分（如 cli/project.py, cli/plc.py, cli/change.py）
- 每个命令组使用 `click.Group` 组织
- 主入口使用 `click.Group` + `add_command` 组装

## 3. 命令定义

- 使用 `@click.command()` 装饰器定义命令
- 使用 `@click.group()` 装饰器定义命令组
- 命令函数名使用 `cmd_` 前缀（如 `cmd_list`, `cmd_create`）
- 命令组函数名使用模块名（如 `project`, `plc`, `change`）

## 4. 参数定义

- 必填参数使用 `@click.argument()`
- 可选参数使用 `@click.option()`
- 选项名使用 `--kebab-case`（如 `--business-line`, `--dry-run`）
- 选项变量名使用 `click.option('--business-line', 'business_line')` 映射为 snake_case
- 布尔选项使用 `is_flag=True`（如 `--debug`, `--json`, `--confirm`）

## 5. 帮助文本

- 命令帮助文本使用函数 docstring（首行简述，空行后详细说明）
- 选项帮助文本使用 `help=` 参数
- 参数帮助文本使用 `type=` 和 `metavar=` 增强可读性

## 6. 工作空间参数

- 所有命令必须接受 `-w`/`--workspace` 参数指定工作空间根目录
- 工作空间参数放在命令组级别，子命令继承
- 工作空间路径验证在 Service 层执行，不在 CLI 层

## 7. 输出格式

- 默认输出人类可读格式（使用 Rich 库增强）
- `--json` 选项输出 JSON 格式（机器可读）
- 错误信息使用 `click.echo()` + `fg='red'`
- 成功信息使用 `click.echo()` + `fg='green'`

## 8. 测试

- 使用 `click.testing.CliRunner` 测试 CLI
- 关键测试: 命令注册、参数解析、帮助文本、错误处理
- 测试隔离: 每个测试用例使用临时目录

## 9. 反模式（禁止）

- 禁止在 CLI 层实现业务逻辑（应委托 Service 层）
- 禁止使用 `sys.argv` 直接解析参数
- 禁止在 CLI 层直接操作数据库
- 禁止硬编码路径（使用 -w 参数或配置文件）
