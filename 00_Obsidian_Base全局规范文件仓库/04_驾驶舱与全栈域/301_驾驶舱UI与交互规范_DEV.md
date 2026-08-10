---
spec_id: CP-301
title: "驾驶舱UI与交互规范"
version: "V1.1.0"
domain: cockpit
lifecycle: stable
canonical_path: "00_Obsidian_Base全局规范文件仓库/04_驾驶舱与全栈域/301_驾驶舱UI与交互规范_DEV.md"
tags: ["驾驶舱", "UI/UX", "SCADA", "HMI", "DJ-2026-005实践"]
changelog:
  - version: V1.1.0
    date: 2026-08-09
    author: Antigravity AI
    changes: 基于 DJ-2026-005 标杆实践融入 11 页 SCADA HMI 控制面板结构、信号状态徽章与原型打包归档 SOP
---

# 301 驾驶舱 UI 与交互规范

## 1. 概述
本规范定义了 008 驾驶舱 (Cockpit) 前端 UI、工业级 SCADA/HMI 控制面板组件结构、数据交互与状态同步的标准规约。

## 2. UI/UX 核心原则
- **深色科技风主题**: 统一采用高对比度、现代化深色模式 (Dark Glassmorphism SCADA UI)。
- **响应式与实时性**: 支持 WebSocket / HTTP Polling 状态实时更新，避免全页刷新。
- **模块化中心架构**:
  - `workspace`: 项目推进与迭代中心
  - `changeCenter`: 变更、缺陷与发布中心
  - `specCenter`: 规范与知识图谱中心 (直接渲染 Obsidian Vault 双向链接)

## 3. 工业级 SCADA/HMI 11 页控制面板规范 (基于DJ-2026-005实践)

标准工业级 HMI 控制面板与 Web 驾驶舱视图，统一采用 11 页标准结构：

| 页面编号 | 页面名称 | 核心功能组件与交互要求 |
|:---|:---|:---|
| **P01** | **系统总览 (Overview)** | 全局设备状态、三色指示灯 (运行/停止/报警)、实时 OEE 仪表盘、工站总切流 |
| **P02** | **自动工艺流程 (Process)** | 顺控流程图、当前 Step 高亮显示、前后端设备信号收发徽章、生产线方向动画 |
| **P03** | **IO 实时监控 (IO Monitor)** | 数字量/模拟量通道状态点阵表、强制 IO 功能、点位英文标识与中文描述 |
| **P04** | **报警管理 (Alarm List)** | 实时报警列表、历史报警追溯、49 类报警码分级、一键复位与声光消除 |
| **P05** | **配方管理 (Recipe)** | 工艺参数配方下载/保存/比对、多型号规格快速切换卡片 |
| **P06~P08** | **机构手动控制 (Manual)** | 轴定位、气缸伸缩单步点动控制、安全联锁防错判定提示 |
| **P09** | **权限管理 (Permission)** | 3 级操作权限控制 (操作员/维护员/管理员)、自动超时登出 |
| **P10** | **通信与总线 (Comm)** | PLC/HMI/MES/机器人通信链路卡片、心跳丢失告警 |
| **P11** | **系统设置 (Settings)** | 语言切换、主题色调调整、离线诊断导出 |

## 4. 原型打包与归档规约
- 研发阶段产出的 HTML/CSS/JS 高保真可交互原型，统一存储于项目 `03_HMI设计/` 目录。
- 每次原型定型或交付，必须使用 CLI 命令打包：
  ```powershell
  auto-pm -w "<工作空间根>" prototype bundle --pid <项目ID> --version <版本号>
  ```
- 早期版本的原型 HTML 文件必须归档至 `03_HMI设计/历史备份/`，禁止直接删除历史变更。
