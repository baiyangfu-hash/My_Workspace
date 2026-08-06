# SW-2026-009 英语学习助手 (English Learning App)

> **专为美国出差与学习场景设计的纯本地离线 Windows 桌面英语学习应用（对标 Busuu）**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Auto-PM Compliance](https://img.shields.io/badge/auto--pm-100%25%20S--Grade-success.svg)](#)

---

## 🌟 项目亮点

1. **纯本地离线运行**：零依赖外部 API，全功能离线词典 (ECDICT)、SAPI5 本地语音合成与 FSRS 记忆卡片算法。
2. **美国出差实战场景**：内置 27+ 涵盖机场海关、交通出行、酒店入住、快餐得来速、星巴克点咖啡等实战对话。
3. **5大 PM 过程组规范治理**：挂载 008 Auto-PM 自动化项目治理框架（启动/规划/执行/监控/收尾/交付物）。
4. **深色玻璃拟物 GUI (PySide6 + QML)**：高清现代 Dark Glassmorphism 界面与平滑交互体验。

---

## 📁 5大过程组架构

```text
SW-2026-009_英语学习助手/
├── 00_项目基础信息/             # 项目治理、规范与立项元数据
├── 01_启动/                     # PRD 产品需求文档
├── 02_规划/                     # UI 交互原型 (HTML) 与 架构设计方案
├── 03_执行/                     # 开发日志与源码记录
├── 04_监控/                     # 自动化测试与驾驶舱监控报告
├── 05_收尾/                     # 版本复盘与归档
├── 06_交付物/                   # PyInstaller 打包二进制与发布包
├── english_learning_app/       # Python 包核心
├── src/                        # 业务服务与 UI 引擎
└── tests/                      # 100% 覆盖率自动化测试套件
```

---

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行自动化测试套件
python tests/run_tests.py

# 启动应用 (QML / Python)
python src/main.py
```
