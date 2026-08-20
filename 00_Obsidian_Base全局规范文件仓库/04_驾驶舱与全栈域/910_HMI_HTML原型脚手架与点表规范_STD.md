---
spec_id: STD-910
title: "HMI HTML 原型脚手架与点表规范"
version: "V1.0.0"
domain: cockpit
lifecycle: stable
canonical_path: "00_Obsidian_Base全局规范文件仓库/04_驾驶舱与全栈域/910_HMI_HTML原型脚手架与点表规范_STD.md"
tags: ["HMI", "HTML原型", "点表映射", "工业组态", "DJ-2026-005"]
changelog:
  - version: V1.0.0
    date: 2026-08-17
    author: Antigravity AI
    changes: 沉淀 DJ-2026-005 工业 HMI HTML 原型实践，规范 1280x800 自适应架构与 PLC DB 双向点表契约
---

# 910 HMI HTML 原型脚手架与点表规范

## 1. 概述与适用范围
本规范适用于所有单机/产线设备的工业 HMI（触摸屏/上位机）交互原型设计。统一采用 **轻量化独立 HTML+CSS+JS 脚手架** 替代传统重量级组态软件，用于在项目早期（PM 阶段）进行工艺走查、状态机对齐和点位定义。

## 2. 核心架构与分辨率标准
- **基准分辨率**：`1280 × 800`（适配主流 ProFace GP4501 / 西门子精智屏 / 威纶通 10/12寸屏）。
- **自适应缩放引擎（`fitToScreen`）**：
  - 外层 `.app-scale-outer` 与内层 `.app-scale-inner`。
  - 通过 CSS `transform: scale(min(availW/1280, availH/800, 1))` 保证在任何 PC 浏览器、平板或投屏中不出现滚动条且不被裁剪。

## 3. 标准 11 画面体系
| 编号 | 画面 ID | 画面名称 | 核心元素与用途 |
|:---|:---|:---|:---|
| 01 | `login` | 登录画面 | 操作员/管理员权限分级、系统名称与 Logo |
| 02 | `main` | 主画面 (概览) | 设备三色状态、当前工步（如 `S23`）、良品统计、稼动率、节拍趋势 |
| 03 | `manual` | 手动控制 | 机构单动（气缸伸缩/电机正反转）、安全联锁防呆提示 |
| 04 | `auto` | 自动运行 | 自动启停/暂停/急停、实时工序流转动画、单周期/连续切换 |
| 05 | `param` | 参数设置 | 轴速度/位置配方、超时时间阈值、修改权限拦截 |
| 06 | `status` | 状态监控 | 伺服轴实际位置/转速/扭矩、传感器模拟量曲线 |
| 07 | `io` | IO监控 | 数字量 DI/DO 点阵卡片（LED 绿/灰动态变色）、强制功能 |
| 08 | `alarm` | 报警管理 | 实时报警横幅、历史报警列表、故障代码与复位指引 |
| 09 | `glue` | 打胶/涂胶交互 | 专机/外协设备握手信号、胶量/温度监测 |
| 10 | `robot` | 机器人交互 | 机器人放料/取料握手位、安全门光幕状态 |
| 11 | `system` | 系统设置 | IP/通信设置、PLC 连接状态、日志导出 |

## 4. 点表映射契约（`hmi_tag_mapping.json`）
每个项目在 `03_HMI设计/` 目录下维护点表映射文件，作为 HMI 与 PLC SCL DB 块的单一真源：
```json
{
  "project_id": "DJ-2026-005",
  "tags": [
    {
      "element_id": "val-actual-pos-x1",
      "scl_db_var": "DB_HMI.ActualPos_X1",
      "data_type": "Real",
      "address": "%MD100",
      "description": "X1轴实际坐标(mm)"
    },
    {
      "element_id": "led-station-ready",
      "scl_db_var": "DB_HMI.StationReady",
      "data_type": "Bool",
      "address": "%M10.0",
      "description": "工站就绪信号"
    }
  ]
}
```

## 5. 样式与视觉基线
- **主题**：工业深色高对比度（主背景 `#1a1d21` / `#0f172a`，卡片 `#1e293b`）。
- **指示灯状态**：
  - 绿色 `led green` (`#10b981`)：正常/运行/已接通
  - 黄色 `led yellow` (`#f59e0b`)：警告/动作中/等待
  - 红色 `led red` (`#ef4444`)：报警/故障/急停
  - 灰色 `led gray` (`#64748b`)：未激活/离线
