---
version: "V1.0.0"
status: "已批准"
created: "2026-06-21"
updated: "2026-06-21"
spec_id: "DEV-216"
domain: "Python开发"
title: "PySide6 GUI 开发规范"
lifecycle: "active"
---

# PySide6 GUI 开发规范

## 文档基础信息

| 项目 | 内容 |
|------|------|
| 文档名称 | PySide6 GUI 开发规范 |
| 文档类型 | DEV |
| 规范编号 | DEV-216 |
| 版本号 | V1.0.0 |
| 创建日期 | 2026-06-21 |
| 状态 | 已批准 |
| 适用范围 | 使用 PySide6 开发桌面 GUI 的 Python 项目 |

## 变更记录

| 日期 | 版本 | 变更类型 | 变更内容 | 变更人员 |
|------|------|---------|---------|---------|
| 2026-06-21 | V1.0.0 | 新增 | 初始版本 | auto-pm |

## 1. 概述

本规范定义使用 PySide6 开发桌面 GUI 应用的编码标准，基于 auto-pm V2.0 实践总结。

## 2. 项目结构

- GUI 模块应放在 `ui/` 包下
- 主窗口类放在 `ui/main_window.py`
- 子模块按功能域划分（如 navigation/project_list/workspace/change_center/dialogs 等）
- 数据模型放在 `ui/models/`

## 3. 命名规范

- 窗口类: `*Window`/`*Dialog`/`*Page`（如 MainWindow, ProjectListPage）
- Widget 类: `*Widget`/`*View`/`*Panel`/`*Tab`（如 ProjectCard, ChangeListPanel）
- Model 类: `*Model`（如 NavModel, ProjectTableModel）
- 信号: `signal_name_changed`（snake_case + 过去分词）
- 槽: `on_signal_name_changed`（on_ + 信号名）

## 4. 信号槽机制

- 使用新式连接语法: `sender.signal.connect(receiver.slot)`
- 避免使用 `pyqtSignal`/`pyqtSlot` 装饰器（PySide6 使用 `Signal`/`Slot`）
- 跨模块通信使用信号槽，不直接调用方法
- 信号参数使用基本类型（str/int/bool/enum），不传递 Widget 对象

## 5. 布局管理

- 优先使用 Layout（QVBoxLayout/QHBoxLayout/QGridLayout），不使用绝对定位
- 复杂布局使用 QWidget + Layout 嵌套
- 留白和间距使用 QMargins 和 spacing 属性
- 响应式布局: 使用 stretch 和 sizePolicy

## 6. 多角色适配

- 定义角色枚举（如 Role.PM/PLC/PYTHON/SPEC_EDITOR）
- 角色-Tab 映射表定义每个角色可见的 Tab
- 角色切换时更新 Tab 可见性和工具栏

## 7. 异步处理

- 耗时操作使用 QThread + Signal 通知主线程
- 不在主线程执行 IO/网络/数据库操作
- 使用 QThreadPool 管理线程池
- 进度反馈使用 QProgressDialog + Signal

## 8. 测试

- 使用 pytest-qt 测试 GUI
- 关键测试: 窗口启动、信号槽连接、角色切换、导航状态机
- 不测试视觉效果（颜色/字体/布局像素）

## 9. 反模式（禁止）

- 禁止在信号槽中传递 Widget 对象
- 禁止在非主线程操作 UI
- 禁止使用 processEvents() 强制刷新
- 禁止硬编码颜色/字体（使用 QPalette/QSS）
