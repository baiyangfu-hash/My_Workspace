# SW-2026-005 PLC项目管理工具

> **版本**: V1.1.0 | **状态**: 活跃开发中 | **Python**: 3.9+ | **GUI**: PyQt5

面向PLC自动化项目的**集成化管理桌面工具**，提供项目管理、代码规范检查、标准文档生成、深度诊断分析等一站式能力。

---

## 快速开始

### 环境要求

- Python 3.9 或更高版本
- Windows 10/11 (推荐)
- PyQt5 5.15+

### 三步启动

```bash
# 1. 进入程序目录
cd SW-2026-005_PLC项目管理工具/03_主程序/01_主程序核心代码

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

> **可选**: 安装 QScintilla 获得ST代码语法高亮: `pip install QScintilla`

---

## 项目结构

```
SW-2026-005_PLC项目管理工具/
├── 00_项目基础信息/                        ← 📋 项目立项与需求文档 (NEW!)
│   ├── 000_通用项目立项表_PM-V1.1.0.md      ← 立项审批表
│   └── 001_产品需求文档_PRD-V1.0.0.md       ← PRD规格说明
│
├── 01_项目文档/                            ← 📚 全生命周期工程文档 (NEW!)
│   ├── 01_启动过程/01_项目立项/             ← 立项阶段索引
│   ├── 02_规划过程/                       ← 技术架构与设计
│   │   ├── 007_架构设计文档_ARCH-V1.0.0.md  ← 系统架构(5层/4大模式)
│   │   ├── 008_详细设计文档_DES-V1.0.0.md   ← 类接口与数据模型
│   │   └── 009_API接口文档_INT-V1.0.0.md    ← 公开API参考手册
│   └── 03_执行过程/                       ← 开发进度与测试报告
│
├── 03_主程序/01_主程序核心代码/              ← 主程序根目录
│   ├── main.py                            ← 程序入口
│   ├── config.py                          ← 应用配置常量
│   ├── requirements.txt                   ← Python依赖
│   │
│   ├── src/                               ← 源代码
│   │   ├── core/                          ← 核心层 (Application/Settings/EventBus)
│   │   ├── ui/                            ← UI层 (MainWindow/Dashboard/Widgets/Dialogs)
│   │   ├── services/                      ← 服务层 (11个业务服务)
│   │   ├── models/                        ← 数据层 (8个数据模型)
│   │   ├── parsers/                       ← 解析器 (ST/Variable/SpecDoc/SCLTest)
│   │   ├── checkers/                      ← 规则引擎 (6类检查器 + 注册表)
│   │   ├── diagnostics/                   ← 诊断分析 (LSP兼容/健康度)
│   │   └── utils/                         ← 工具函数 (Logger/FileUtils/PathResolver)
│   │
│   ├── tests/                             ← 单元测试 (14个测试模块)
│   └── resources/                         ← 静态资源 (图标/QSS样式/字体)
│
├── 05_docs/                               ← [归档] 旧版技术文档(已迁移至01_项目文档/)
└── .trae/specs/                           ← 规范与计划文档
```

---

## 核心功能

| # | 功能模块 | 说明 |
|---|----------|------|
| 1 | **仪表盘** | 项目概览、最近项目、健康度评分、快捷操作入口 |
| 2 | **项目管理** | 新建(M001/S001模板)/打开/关闭项目、项目树浏览 |
| 3 | **ST代码编辑器** | SCL语法高亮、代码片段库(case/fb/for/if/move/ton) |
| 4 | **HMI变量映射** | PLC变量→HMI标签映射管理、IO信号表编辑 |
| 5 | **规范检查面板** | 命名/语法/注释/配置/定时器/变量 六维检查 |
| 6 | **诊断面板** | 七维度深度诊断、LSP兼容性检查、修复建议 |
| 7 | **测试运行器** | SCLTest解析执行、测试用例管理与结果查看 |
| 8 | **文档生成** | 10种标准模板(ALM/ARC/CHG/DSN/IFC/IO/REQ/UM/VAR) |
| 9 | **变量检查器** | PLC变量规范性校验(I/O地址/命名/类型) |
| 10 | **路径解析器** | 策略模式实现，支持相对/绝对路径自动转换 |

---

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.9+ |
| GUI框架 | PyQt5 | ≥5.15 |
| 代码编辑 | QScintilla | ≥2.13 (可选) |
| 日志系统 | loguru | ≥0.7 |
| Excel处理 | openpyxl | ≥3.0 |
| 数据验证 | pydantic | ≥2.0 |
| 测试框架 | pytest + pytest-qt | ≥7.0 |

---

## 开发者导航

| 文档 | 路径 | 用途 |
|------|------|------|
| **项目立项表** | [00_项目基础信息/000_通用项目立项表_PM-V1.1.0.md](00_项目基础信息/000_通用项目立项表_PM-V1.1.0.md) | 立项审批与范围定义 |
| **产品需求文档(PRD)** | [00_项目基础信息/001_产品需求文档_PRD-V1.0.0.md](00_项目基础信息/001_产品需求文档_PRD-V1.0.0.md) | 功能需求与非功能需求规格 |
| **架构设计文档** | [01_项目文档/02_规划过程/007_架构设计文档_ARCH-V1.0.0.md](01_项目文档/02_规划过程/007_架构设计文档_ARCH-V1.0.0.md) | 系统架构与模块设计(5层/4大模式) |
| **详细设计文档** | [01_项目文档/02_规划过程/008_详细设计文档_DES-V1.0.0.md](01_项目文档/02_规划过程/008_详细设计文档_DES-V1.0.0.md) | 类接口与数据模型定义 |
| **API接口文档** | [01_项目文档/02_规划过程/009_API接口文档_INT-V1.0.0.md](01_项目文档/02_规划过程/009_API接口文档_INT-V1.0.0.md) | 公开API参考手册(7大类) |
| **执行进度跟踪** | [01_项目文档/03_执行过程/README.md](01_项目文档/03_执行过程/README.md) | Sprint进度/功能状态/测试统计 |
| 用户操作手册 | [docs/user_manual.md](docs/user_manual.md) | 功能使用说明 |
| 代码结构说明 | [docs/02_技术文档/010_代码结构说明_DEV-V1.0.0.md](docs/02_技术文档/010_代码结构说明_DEV-V1.0.0.md) | 目录与文件职责 |
| 环境搭建指南 | [docs/03_开发指南/011_开发环境搭建指南_DEV-V1.0.0.md](docs/03_开发指南/011_开发环境搭建指南_DEV-V1.0.0.md) | 开发环境配置 |

---

## 规范遵循

本项目的编码规范遵循:
- [[210_Python编程规范]](../../../01_Project自动化项目管理/00_通用规范/Python开发/210_Python编程规范_DEV-V1.1.0.md)
- [[211_Python代码审查规范]](../../../01_Project自动化项目管理/00_通用规范/Python开发/211_Python代码审查规范_DEV-V1.0.0.md)

项目管理流程遵循全局规范仓库 `00_Obsidian_Base全局规范文件仓库` 的PM域规范。

---

## 模块统计

| 层级 | 模块数 | 文件数 | 核心类 |
|------|--------|--------|--------|
| core/ 核心层 | 6 | 6 | Application, SettingsManager, EventBus |
| ui/ 表现层 | 4 | 16 | MainWindow, Dashboard, *Widget(9), *Dialog(4) |
| services/ 服务层 | 11 | 11 | ProjectService, DiagnosticService 等 |
| models/ 数据层 | 8 | 8 | Project, Document, Template, Variable 等 |
| parsers/ 解析层 | 4 | 4 | STParser, VariableParser 等 |
| checkers/ 规则层 | 7 | 7 | BaseChecker + 6种具体检查器 |
| diagnostics/ 诊断层 | 2 | 2 | LSPCompatibilityChecker, HealthAnalyzer |
| utils/ 工具层 | 4 | 4 | Logger, FileUtils, PathResolver, Validators |
| tests/ 测试层 | - | 14 | test_* 系列 |
| **合计** | **46** | **~72** | |

---

*最后更新: 2026-05-08 | 维护者: AI Assistant*
