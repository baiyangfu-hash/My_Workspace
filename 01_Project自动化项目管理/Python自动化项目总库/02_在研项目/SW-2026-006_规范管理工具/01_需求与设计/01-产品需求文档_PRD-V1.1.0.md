# 产品需求文档 (PRD)

## 文档基础信息

| 字段 | 值 |
|------|-----|
| 项目编号 | SW-2026-006 |
| 项目名称 | 规范管理工具 (SpecMgr) |
| 版本 | V1.1.0 |
| 日期 | 2026-05-25 |
| 负责人 | fubai |

---

## 1. 项目背景

在多技术栈工作空间（PM/PLC/Python）中，规范文件散落在3个目录，存在版本漂移、索引过时、废弃规范仍被引用等问题。前期已建立 `spec_registry.json` 注册表和4个独立Python脚本（spec_health_checker.py、generate_index.py、add_frontmatter.py、generate_metadata_report.py），但它们：

- 分散在Obsidian文档仓库中，代码与文档混杂
- 无统一CLI入口，需分别运行4个python文件
- 无包结构，不可pip安装
- 无单元测试
- 无法被其他工具（如SW-2026-005）集成调用
- 仅CLI交互，不便于向其他工作人员展示和推广

## 2. 产品定位

**一句话定位**：规范管理体系的一站式管理工具（CLI + GUI）

**目标用户**：
1. 开发者本人 — 日常维护规范时使用
2. AI助手（Trae IDE） — 通过CLI接口调用检查和生成功能
3. CI/CD流程 — 作为门禁工具自动检查规范健康
4. 其他工作人员 — 通过GUI界面直观操作，降低使用门槛

**不做**：
- 不做Obsidian插件
- 不做Web界面（B/S架构）
- 不做规范内容编辑器
- 不做规范文件的版本控制（由Git负责）
- 不做多用户并发/权限管理（单人本地使用）

## 3. 功能需求

### 3.1 核心命令（V0.1.0 MVP — CLI）

| 命令 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `specmgr check` | 规范健康检查 | workspace路径 | 检查报告（终端输出） |
| `specmgr index` | 索引自动生成 | workspace路径 + domain过滤 | 更新3个INDEX文件 |
| `specmgr frontmatter` | 批量添加frontmatter | workspace路径 + dry-run选项 | 修改规范文件 |
| `specmgr report` | 元数据汇总报告 | workspace路径 | 生成报告.md |

### 3.2 check 子命令详细需求

| 检查项ID | 检查内容 | 严重级别 | MVP |
|----------|----------|----------|-----|
| SHC-001 | 同一规范ID在多个位置存在活跃副本 | ERROR | ✅ |
| SHC-002 | 规范文件版本与注册表记录不一致 | ERROR | ✅ |
| SHC-003 | deprecated规范仍被其他文件引用 | WARNING | ✅ |
| SHC-004 | INDEX中列出的文件实际不存在 | ERROR | ✅ |
| SHC-005 | 实际存在的规范未在INDEX中列出 | WARNING | ✅ |
| SHC-006 | Obsidian [[链接]]指向不存在的文件 | WARNING | ✅ |
| SHC-007 | 规范文件缺少必要frontmatter | INFO | ✅ |
| SHC-008 | .trae/rules中引用的规范路径无效 | ERROR | ✅ |

输出格式：
- 终端：彩色表格（🔴错误/🟡警告/🟢提示）
- JSON：`specmgr check --format json` 供程序调用
- 退出码：0=全部通过，1=有错误，2=仅有警告

### 3.3 index 子命令详细需求

- 从 `spec_registry.json` 生成3个INDEX文件：
  - `00_Obsidian_Base全局规范文件仓库/00_INDEX_全局规范索引_V2.0.0.md`
  - `0100_PLC自动化/00_通用规范/README.md`
  - `01_Project自动化项目管理/00_通用规范/README.md`
- 支持 `--domain pm/plc/python` 只生成指定域
- 生成的INDEX文件头部标注"自动生成，请勿手动编辑"

### 3.4 frontmatter 子命令详细需求

- 从 `spec_registry.json` 读取元数据，为缺少frontmatter的活跃规范添加YAML头
- `--dry-run` 选项：仅预览不修改
- 跳过已有frontmatter的文件和deprecated/archived文件

### 3.5 report 子命令详细需求

- 生成规范元数据汇总报告
- 包含：总览统计、按域分布、替代关系图(Mermaid)、按域分类表、完整YAML清单
- 输出到 `00_Obsidian_Base全局规范文件仓库/规范元数据汇总报告.md`

### 3.6 全局选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--workspace` | 工作空间根目录 | 当前目录或配置文件中的值 |
| `--config` | 配置文件路径 | `specmgr.yaml` 或 `.specmgr.yaml` |
| `--verbose` | 详细输出 | False |
| `--quiet` | 静默模式 | False |

### 3.7 GUI界面需求（V0.3.0+）

#### 3.7.1 GUI总体要求

- 基于PySide6构建桌面GUI应用
- 与CLI共享核心业务逻辑（通过Service层调用）
- 支持打包为独立exe，免安装直接运行
- 界面语言：中文

#### 3.7.2 GUI页面设计

| 页面 | 功能 | 关键交互 |
|------|------|----------|
| 仪表盘 | 规范总览、健康状态统计 | 统计卡片(总数/活跃/废弃)、最近检查结果摘要 |
| 健康检查 | 运行检查、查看结果 | 运行按钮、结果表格(可按严重级别筛选)、详情面板、修复建议 |
| 索引生成 | 生成/更新索引文件 | 域选择(多选)、生成按钮、进度指示、预览结果 |
| Frontmatter管理 | 批量管理frontmatter | 文件列表、前后对比预览、dry-run/执行切换 |
| 报告生成 | 生成元数据报告 | 格式选择(MD/JSON)、输出路径、预览 |
| 设置 | 工作空间配置 | 路径选择器、配置项编辑、保存/重置 |

#### 3.7.3 GUI非功能需求

| 需求 | 说明 |
|------|------|
| 响应性 | 耗时操作(检查/生成)使用QThread，不阻塞UI |
| 状态反馈 | 操作进度条、完成提示、错误提示 |
| 窗口大小 | 默认1200x800，可调整，记住窗口位置和大小 |
| 启动方式 | `specmgr gui` 命令或直接运行exe |

### 3.8 打包分发需求（V0.5.0+）

| 需求 | 说明 |
|------|------|
| 打包格式 | 单目录分发（含exe+依赖），可选单文件exe |
| 打包工具 | PyInstaller |
| 目标平台 | Windows (x64) |
| 体积控制 | 目标 < 100MB |
| 启动速度 | 冷启动 < 5秒 |
| 无需安装 | 解压/复制即可运行，无需Python环境 |

## 4. 非功能需求

| 需求 | 指标 |
|------|------|
| 性能 | check命令在100个规范文件的工作空间中 < 5秒 |
| 可安装 | 支持 `pip install -e .` 开发模式安装 |
| Python版本 | >= 3.9 |
| 依赖 | click + PySide6 + pyyaml（轻量依赖） |
| 可测试 | 核心逻辑测试覆盖率 > 80% |
| 可集成 | JSON输出格式供其他工具调用 |
| 可分发 | 打包为exe，免安装运行 |

## 5. 数据模型

核心数据文件：`spec_registry.json`

```json
{
  "version": "1.0.0",
  "last_updated": "2026-05-24",
  "workspace_root": "绝对路径",
  "domains": { "pm": "...", "plc": "...", "python": "...", "cross-domain": "..." },
  "lifecycle_states": { "stable": "...", "draft": "...", "deprecated": "...", "archived": "..." },
  "specs": {
    "SPEC-ID": {
      "title": "规范标题",
      "number": "编号",
      "canonical_path": "相对路径",
      "version": "VX.Y.Z",
      "type_prefix": "类型前缀",
      "domain": "归属域",
      "lifecycle": "生命周期状态",
      "sub_domain": "子域",
      "tags": ["标签"],
      "replaces": ["替代的规范ID"],
      "replaced_by": ["被替代的规范ID"]
    }
  },
  "project_copies": [
    {
      "spec_id": "规范ID",
      "project": "项目编号",
      "path": "项目级副本路径",
      "actual_version": "实际版本",
      "drift_detected": true
    }
  ]
}
```

## 6. 里程碑

| 版本 | 目标 | 范围 |
|------|------|------|
| V0.1.0 | CLI MVP | 4个核心CLI命令可用，从现有脚本迁移 |
| V0.2.0 | Service层重构 | 从commands提取业务逻辑到services，CLI调用services |
| V0.3.0 | GUI MVP | PySide6基本框架+仪表盘+健康检查页 |
| V0.4.0 | GUI完善 | 索引/Frontmatter/报告/设置页 |
| V0.5.0 | 打包分发 | PyInstaller打包exe，免安装运行 |
| V1.0.0 | 正式发布 | 完善文档、测试覆盖率>80%、与SW-2026-005集成 |

## 7. 验收标准

### V0.1.0 MVP验收

1. `pip install -e .` 安装后，`specmgr --help` 可用
2. `specmgr check --workspace <path>` 输出8项检查结果
3. `specmgr check --workspace <path> --format json` 输出JSON格式
4. `specmgr index --workspace <path>` 生成3个INDEX文件
5. `specmgr frontmatter --workspace <path> --dry-run` 预览模式
6. `specmgr report --workspace <path>` 生成汇总报告
7. pytest测试通过
8. 00_Obsidian_Base中的4个脚本标记为废弃，指向specmgr

### V0.3.0 GUI MVP验收

1. `specmgr gui` 启动GUI窗口
2. 仪表盘显示规范统计信息
3. 健康检查页可运行检查并显示结果
4. 检查结果可按严重级别筛选
5. 耗时操作不阻塞UI

### V0.5.0 打包验收

1. PyInstaller打包生成可执行文件
2. 在无Python环境的Windows机器上可正常运行
3. 冷启动时间 < 5秒
