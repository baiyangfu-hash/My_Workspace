---
version: "V1.1.0"
status: "历史发布记录"
created: "2026-08-17"
updated: "2026-09-01"
spec_id: "RELEASE_NOTES"
project_id: "SW-2026-008"
---

# auto-pm 自动化项目管理工具 - 版本发布说明 (RELEASE_NOTES)

> **当前版本**：`V1.1.0`  
> **发布日期**：`2026-08-17`  
> **适用平台**：Windows 10/11 x64 (免安装绿色包 / Python 3.11+)

> 2026-09-01 治理备注：本文保留为 `V1.1.0` 历史发布记录；当前源码基线为 `V1.2.3`，默认运行入口已迁至 `00_Infrastructure/auto_pm`。本次文档资产整理未重新生成 `V1.2.3` 对外发布包。

---

## 1. 版本概述

`auto-pm` V1.1.0 完成了系统源码 Clean Architecture 5 大物理分层重构（Contracts / Domain / Infrastructure / Application / UI），引入了 5 大过程组阶段门禁规则引擎，并对全景 GUI 交互与 18 个弹窗遮罩进行了地毯式加固。

---

## 2. 核心特性与增强矩阵

- **Clean Architecture 5 层物理分层 (CHG-SCPT-2026-159)**：彻底消除平铺包目录，后端单测累计达 **1585 项，100% 绿灯通过**。
- **阶段门禁规则引擎 (CHG-SCPT-2026-158)**：实现 G1~G4 多维自动评估。
- **全景 GUI 交互与弹窗深度矩阵加固 (CHG-SCPT-2026-160)**：全量 18 个弹窗采用 `#0f172a` 实底面板与 `#b3000000` 70% 暗场遮罩，消灭文字穿透；全量接入 `PrimaryButton` 动效；20 维全景真机测试全绿。

---

## 3. 发布放行签署

- **单元测试验证**：`1585 passed / 0 failed` ✅
- **GUI 交互验证**：`20 / 20 passed (0 error / 0 warning)` ✅
- **规范门禁自检**：`SHC-011 ~ SHC-014 ALL PASS` ✅
