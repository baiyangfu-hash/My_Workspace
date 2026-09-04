# Spec: 交付物打包系统性修复

## 1. 背景与目标

### 1.1 问题背景

2026-04-15当天，Python项目管理工具经历了**4次发布尝试，3次出错**：

| 版本 | 错误 | 直接原因 |
|------|------|---------|
| V2.4.1 (豆包) | zip仅21KB缺核心程序 | AI跳过大目录 |
| V2.4.1 (修复) | PowerShell中文路径失败 | 编码不兼容 |
| V2.4.2 | 模板旧版+exe未重编译 | 流程缺失 |
| V2.4.3 (第一次) | zip仅12文件57MB | 又用了Compress-Archive |

### 1.2 根因诊断

经审查全局规范仓库中的 `220_Python项目打包规范_DEV-V2.1.0.md`（1117行），发现：

**规范质量高但执行力为零**，具体5个缺陷：

| # | 缺陷 | 规范位置 | 后果 |
|---|------|---------|------|
| D1 | 内部自相矛盾 | L526 vs L729 | 执行者不知该听哪个 |
| D2 | 目录结构过时 | L438-467 | 与实际项目不匹配 |
| D3 | 阈值数据不准 | L895-902 | 验证误报/漏报 |
| D4 | 无可执行代码 | 全文 | 只能靠人自觉遵守 |
| D5 | 项目未引用 | 项目自身 | AI执行时不知道规范存在 |

### 1.3 目标

1. **修复全局规范**的5个缺陷（D1-D5）
2. **创建统一构建脚本** `scripts/build_delivery.py` 作为唯一入口
3. **验证V2.4.3** 通过新脚本重新打包确认正确性

---

## 2. 修复范围

### 2.1 全局规范修改

**文件**: `00_Obsidian_Base全局规范文件仓库/03_执行过程/02_部署交付/01_部署规范/220_Python项目打包规范_DEV-V2.1.0.md`
**目标版本**: V2.2.0

| 修改项 | 当前内容 | 修改为 | 原因(D#) |
|--------|---------|--------|----------|
| L526 打包工具 | "使用 Compress-Archive 或 7z 生成ZIP" | "使用 Python zipfile.ZIP_DEFLATED 生成ZIP（见15.2.2）" | D1: 消除矛盾 |
| L438-467 目录结构 | 8目录(01源代码~08交付清单) | 对齐项目实际6目录结构 | D2: 与实际一致 |
| L897 ZIP正常范围 | "100-110 MB" | "150-170 MB (PyInstaller onedir模式)" | D3: 数据准确 |
| 新增附录 | 无 | 提供完整可运行的build_delivery.py源码 | D4: 代码强制 |

### 2.2 项目新增文件

| 文件 | 用途 |
|------|------|
| `03_主程序/01_主程序核心代码/scripts/build_delivery.py` | 统一构建入口脚本 |

### 2.3 不修改的内容

- 不修改现有业务代码（template_service.py, base.py等已修复完成）
- 不改变06_交付物/的目录结构
- 不修改PyInstaller编译配置

---

## 3. 详细设计

### 3.1 build_delivery.py 脚本设计

```python
# scripts/build_delivery.py — 统一交付物构建脚本
#
# 用法:
#   python build_delivery.py --version V2.4.3          # 完整流程(编译+更新+打包+验证)
#   python build_delivery.py --version V2.4.3 --skip-build  # 跳过编译
#   python build_delivery.py --version V2.4.3 --verify-only # 仅验证已有zip
#
# 流程:
#   [1] 编译检查(PyInstaller)  → [2] 更新06_交付物/
#   → [3] 校验交付物完整性    → [4] 打包zip(Python zipfile)
#   → [5] 校验zip(7项CHK)     → [6] 输出报告
```

#### 3.1.1 配置区（硬编码项目路径）

```python
CONFIG = {
    "base_dir": r"d:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\..."
    "src_code": "03_主程序/01_主程序核心代码",
    "delivery": "06_交付物",
    "pack_dir": "06_交付物打包",
    "release_notes": "02_发布说明",
    "product_name": "Python自动化项目管理系统",
    "exe_name": "Python项目管理工具.exe",
}
```

#### 3.1.2 Step 1: 编译检查（可选）

- 检查 `dist/{exe_name}` 存在且 >50MB
- 如不存在或 `--no-skip-build`，自动调用 PyInstaller
- 编译失败则终止并报错

#### 3.1.3 Step 2: 更新交付物目录

按以下映射复制文件：

| 源 | 目标 | 必需 |
|----|------|:----:|
| `dist/*.exe` | `01_可执行文件/*.exe` | ✅ |
| `dist/_internal/*` | `01_可执行文件/_internal/*` | ✅ |
| `config/*.json` | `01_可执行文件/config/*.json` | ✅ |
| `data/project_manager.db` | `data/project_manager.db` | ✅ |
| `02_发布说明/V{x.y.z}*.md` | `02_发布说明/` | ✅ |
| `02_发布说明/01_交付清单*.md` | `02_发布说明/` 或 根目录 | ✅ |

复制后校验：
- exe > 50MB
- _internal/ 有 >400 文件
- config/ 有 4 个json
- db 存在

#### 3.1.4 Step 3: 交付物目录校验

```python
DELIVERY_CHECKS = [
    ("exe_exists", lambda: exe_path.exists() and exe_size > 50*MB),
    ("internal_exists", lambda: internal_count >= 400),
    ("config_count", lambda: config_count == 4),
    ("db_exists", lambda: db_path.exists()),
    ("docs_exist", lambda: doc_count >= 2),
    ("total_files", lambda: total_file_count >= 900),
]
```

任何一项FAIL → 终止，不进入打包步骤。

#### 3.1.5 Step 4: 打包zip（强制Python zipfile）

```python
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(delivery_dir):
        for fn in files:
            fp = os.path.join(root, fn)
            arcname = os.path.relpath(fp, delivery_dir)
            zf.write(fp, arcname)
```

**关键规则**：
- ❌ 不使用 PowerShell Compress-Archive
- ❌ 不使用 7z 命令行
- ✅ 仅使用 Python 标准库 zipfile

#### 3.1.6 Step 5: ZIP校验（7项CHK）

复用规范V2.1.0第17节的验证逻辑，更新阈值：

| CHK编号 | 检查项 | 最小 | 正常范围 | 最大 | V2.4.3实际值 |
|:-------:|--------|:----:|----------|:----:|:-----------:|
| CHK-001 | 总文件数 | 500 | 940-960 | 1500 | 951 |
| CHK-002 | ZIP大小(MB) | 80 | 155-165 | 200 | 160.13 |
| CHK-003 | exe大小(MB) | 10 | 55-62 | 100 | ~58 |
| CHK-004 | _internal文件数 | 400 | 850-900 | 1200 | 882 |
| CHK-005 | 关键文档数 | 3 | 5-10 | 20 | 5 |
| CHK-006 | 配置文件数 | 4 | 4 | 4 | 4 |
| CHK-007 | 一级目录含01_可执行文件 | - | 存在 | - | ✅ |

#### 3.1.7 Step 6: 输出报告

```
============================================================
DELIVERY BUILD REPORT - V{版本}_{日期}
============================================================
Step 1 [编译]:  ✅ PASS / ⏭ SKIPPED / ❌ FAIL
Step 2 [更新]:  ✅ PASS (复制N个文件)
Step 3 [校验]:  ✅ PASS (M/N checks)
Step 4 [打包]:  ✅ PASS ({文件数} files, {大小}MB)
Step 5 [验证]:  ✅ PASS (🟢 7/7 CHK)

>>> Final Status: 🟢 RELEASE APPROVED
============================================================
```

### 3.2 全局规范修改详情

#### 修改D1: L526 打包工具（消除矛盾）

**原文(L526)**:
```
4. **打包阶段**: 使用 Compress-Archive 或 7z 生成 ZIP
```

**改为**:
```
4. **打包阶段**: 使用 Python zipfile.ZIP_DEFLATED 生成 ZIP
                    （详见第15.2.2节技术栈推荐，禁止使用PowerShell Compress-Archive）
```

#### 修改D2: L438-467 目录结构（对齐实际）

**原文**定义8个一级目录（01_源代码~08_交付清单），改为对齐项目实际的6个主要目录+散落文件：

```
压缩包内部结构（本项目实际版）：
{系统名称}_V{版本号}_{日期}.zip/
├── 01_可执行文件/              # 必须: exe + _internal/ + config/
├── 02_发布说明/                # 必须: 更新说明 + 交付清单
├── 02_配置文件/                # 可选: config副本
├── 03_测试文件/                # 可选: 测试脚本
├── 04_文档/                    # 可选: README等
├── 05_数据库/                  # 可选: db备份
├── data/                       # 必须: project_manager.db
├── *.md                        # 散落文档(README,已知问题等)
└── *.ps1                       # 散落脚本(如有)
```

#### 修改D3: L897 ZIP阈值（数据准确）

**原文**:
```
| **ZIP文件大小** | 80 MB | 100-110 MB | 200 MB |
```

**改为**:
```
| **ZIP文件大小** | 80 MB | 150-170 MB | 200 MB |
```

备注增加：`(PyInstaller onedir模式含_internal依赖，实际约160MB)`

#### 修改D4: 新增附录 — 完整构建脚本

在附录15之后新增：

```
## 附录A: 标准构建脚本 build_delivery.py（V2.2.0新增）

> 本附录提供完整可运行的构建脚本源码，作为本规范的强制性执行工具。
> 所有打包操作必须通过此脚本执行，禁止临时手写脚本替代。

[此处嵌入 build_delivery.py 完整源码]
```

---

## 4. 任务分解

### Task 1: 创建 build_delivery.py 脚本
- 文件: `03_主程序/01_主程序核心代码/scripts/build_delivery.py`
- 实现6步完整流程
- 含命令行参数解析(--version, --skip-build, --verify-only)
- 含7项CHK验证逻辑
- 含彩色终端输出报告

### Task 2: 修复全局规范220_V2.1.0 → V2.2.0
- 修改D1: L526消除Compress-Archive矛盾
- 修改D2: L438-467目录结构对齐实际
- 修改D3: L897 ZIP阈值更新
- 修改D4: 新增附录A（构建脚本源码）
- 更新版本号为V2.2.0
- 更新变更记录

### Task 3: 用新脚本验证V2.4.3
- 运行 `python build_delivery.py --version V2.4.3 --skip-build`
- 确认输出报告全部PASS
- 对比新生成的zip与当前V2.4.3 zip一致

### Task 4: 清理残留临时文件
- 删除 `_diagnose_templates.py`, `_list_tables.py`
- 删除 `_self_test_*.py` (3个)
- 确认06_交付物根目录散落的ps1/md文件是否需要清理

---

## 5. 验收标准

- [ ] AC-01: `build_delivery.py` 可一键执行完整构建流程
- [ ] AC-02: 脚本强制使用Python zipfile，不含任何PowerShell调用
- [ ] AC-03: 7项CHK验证全部实现，阈值与实际数据匹配
- [ ] AC-04: 全局规范更新至V2.2.0，D1-D4缺陷全部修复
- [ ] AC-05: V2.4.3通过新脚本验证，报告显示🟢 RELEASE APPROVED
- [ ] AC-06: 临时测试文件已清理

---

## 6. 风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|:----:|:----:|------|
| 规范修改影响其他项目 | 低 | 中 | 仅修改目录结构和阈值，不改核心流程 |
| 构建脚本路径硬编码 | 中 | 低 | 脚本内注释说明，后续可改配置文件 |
