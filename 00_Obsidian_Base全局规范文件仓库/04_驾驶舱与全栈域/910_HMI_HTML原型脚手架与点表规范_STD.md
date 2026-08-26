---
spec_id: STD-910
title: "HMI HTML 原型脚手架与标准部件库规范"
version: "V2.0.0"
domain: cockpit
lifecycle: stable
canonical_path: "00_Obsidian_Base全局规范文件仓库/04_驾驶舱与全栈域/910_HMI_HTML原型脚手架与点表规范_STD.md"
tags: ["HMI", "HTML原型", "WebComponents", "标准部件库", "点表映射", "工业组态", "DJ-2026-005"]
changelog:
  - version: V2.0.0
    date: 2026-08-24
    author: Antigravity AI
    changes: 工业级标准图形部件库与 Design Tokens 体系下沉，固化 Web Components 自定义组件标签与模型驱动组装契约
  - version: V1.0.0
    date: 2026-08-17
    author: Antigravity AI
    changes: 沉淀 DJ-2026-005 工业 HMI HTML 原型实践，规范 1280x800 自适应架构与 PLC DB 双向点表契约
---

# 910 HMI HTML 原型脚手架与标准部件库规范

## 1. 概述与适用范围
本规范适用于所有单机/产线设备的工业 HMI（触摸屏/上位机）交互原型设计。统一采用 **轻量化标准 Web Components 图形部件库 + Design Tokens 样式库 + 独立 HTML 脚手架** 替代传统随意编码与重量级组态软件，确保所有项目人机界面风格 100% 统一、组件零自由发挥、完全模型驱动。

## 2. 核心架构与分辨率标准
- **基准分辨率**：`1280 × 800`（适配主流 ProFace GP4501 / 西门子精智屏 / 威纶通 10/12寸屏）。
- **自适应缩放引擎（`fitToScreen`）**：
  - 外层 `.app-scale-outer` 与内层 `.app-scale-inner`。
  - 通过 CSS `transform: scale(min(availW/1280, availH/800, 1))` 保证在任何 PC 浏览器、平板或投屏中不出现滚动条且不被裁剪。

## 3. 标准 11 画面体系
| 编号 | 画面 ID | 画面名称 | 核心元素与用途 |
|:---|:---|:---|:---|
| 01 | `login` | 登录画面 | 操作员/工程师/管理员权限分级、虚拟 PIN 码键盘 |
| 02 | `main` | 主画面 (概览) | 2.5D SVG 数字孪生机械总图、伺服 DRO、节拍/OEE 看板、首出报警横条 |
| 03 | `manual` | 手动控制 | 机构单动（气缸伸缩/电机正反转/伺服 JOG）、3 轴回原点 |
| 04 | `auto` | 自动运行 | 自动启停/暂停/急停、三工站状态机甘特时序流、单步/单周期模式 |
| 05 | `param` | 参数设置 | 伺服轴目标位置一键教导 (D510~D630)、速度加速度、超时时间阈值 |
| 06 | `status` | 状态监控 | 伺服轴黄金信号 (位置/转速/扭矩/滞后误差)、8 路安全门矩阵 |
| 07 | `io` | IO监控 | 全量 71 DI / 48 DO 物理端子排卡片（LED 绿/灰动态变色）、强制仿真功能 |
| 08 | `alarm` | 报警管理 | 实时报警横幅、MES 10条去重队列、点击直接弹出故障排查 SOP |
| 09 | `glue` | 打胶/涂胶交互 | STD-820 8 步握手状态机、Y47 安全区互锁波形仿真 |
| 10 | `robot` | 机器人交互 | 机器人放料/取料握手位、4 层料仓满料/叫料调度指示 |
| 11 | `system` | 系统设置 | IP/以太网 MC 通信设置、PLC 固件版本信息、CSV 日志导出 |

## 4. 标准 Web Components 图形部件库契约 (`hmi-components.js`)
所有项目原型页面必须使用统一的标准组件标签组装，严禁手写非标杂乱 HTML：

1. `<hmi-dro label="..." unit="..." tag="..." value="..."></hmi-dro>`：数显表盘 / 坐标徽章；
2. `<hmi-led color="green|yellow|red|cyan" state="on|off|blink"></hmi-led>`：工业高对比度指示灯；
3. `<hmi-btn type="primary|success|warning|danger" size="sm|md|lg"></hmi-btn>`：工业触感控制按钮；
4. `<hmi-axis-dro axis-name="Z轴" pos-reg="D101" vel-reg="D320"></hmi-axis-dro>`：伺服轴黄金信号综合表盘；
5. `<hmi-cylinder name="阻挡气缸" up-io="X31" down-io="X32" sol-io="Y44"></hmi-cylinder>`：气缸双位置控制单元；
6. `<hmi-conveyor-unit layer="1" speed-reg="D300" motor-io="Y30"></hmi-conveyor-unit>`：单层变频输送机控制单元；
7. `<hmi-terminal-strip module="CPU_DI" points="..."></hmi-terminal-strip>`：真实端子排与强制仿真组件；
8. `<hmi-step-flow station="1" steps="..."></hmi-step-flow>`：状态机时序流甘特组件；
9. `<hmi-handshake spec="STD-820" req-io="Y44" ack-io="X76"></hmi-handshake>`：外协设备标准握手波形组件；
10. `<hmi-numpad-modal></hmi-numpad-modal>`：触控数字小键盘；
11. `<hmi-sop-modal></hmi-sop-modal>`：电气故障排障 SOP 交互弹窗。

## 5. Design Tokens 样式规范 (`hmi-tokens.css`)
- **调色板语义**：
  - 主背景：`--bg-dark: #0f131a;` / 面板：`--bg-panel: #171d27;` / 卡片：`--bg-card: #1f2735;`
  - 运行绿：`--success: #00e676;` (0 0 8px rgba(0, 230, 118, 0.4))
  - 警告黄：`--warning: #ffb300;` (0 0 8px rgba(255, 179, 0, 0.4))
  - 故障红：`--danger: #ff3d00;` (0 0 8px rgba(255, 61, 0, 0.4))
  - 极光青：`--cyan: #00e5ff;` (DRO 专用高亮数显)
  - 工业蓝：`--primary: #0088ff;`

## 6. 点表映射契约（`hmi_tag_mapping.json`）
每个项目在 `03_HMI设计/` 目录下维护点表映射文件，作为 HMI 与 PLC SCL DB 块的单一真源。必须覆盖全部 PLC 变量与物理 IO 地址。
