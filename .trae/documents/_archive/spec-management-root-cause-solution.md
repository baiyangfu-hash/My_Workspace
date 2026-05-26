# 规范管理体系根治方案

> **版本**: V1.0.0
> **日期**: 2026-05-24
> **目标**: 从根源上解决规范管理的碎片化、漂移和同步问题，建立长期可靠的体系

---

## 一、根因诊断：6个深层问题

通过全面扫描工作空间，我发现了以下**根源性问题**（不是表面症状）：

### 问题1：副本式分发导致版本漂移 🔴 严重

**现象**：同一规范文件存在于多个位置，版本不一致

**实证**：`801_PLC变量命名与功能块命名规范` 存在于3个位置：
| 位置 | 版本 | 状态 |
|------|------|------|
| `0100_PLC自动化/DJ-2026-005/01_需求与设计/10_编程及变量规范/` | **V1.0.7** | 活跃（最新） |
| `00_Obsidian_Base全局规范文件仓库/_archive/deprecated/` | V1.0.5 | 归档 |
| `00_Obsidian_Base全局规范文件仓库/_archive/2026-04-23_版本清理/` | V1.0.2 | 归档 |

**根因**：规范采用"复制分发"模式而非"引用分发"模式。每次迁移都是复制，原副本不删除或不同步，导致同一规范有N个版本在N个位置独立演化。

### 问题2：.trae/rules 与 Obsidian 规范体系脱节 🔴 严重

**现象**：AI助手不知道技术栈规范在哪里，也不知道规范的具体内容

**实证**：
- `.trae/rules/` 仅有3个文件（Claude.md、git-commit-message.md、project-rule.md），全部在工作空间根目录
- `0100_PLC自动化/` 和 `01_Project自动化项目管理/` 下**没有** `.trae/rules/`
- AI助手在PLC项目中工作时，不知道 `905_SCL编程规范` 的存在和位置
- `project-rule.md` 中PLC特定规则（如`libraries`字段名）与通用规则混在一起

**根因**：.trae规则体系是扁平的（仅workspace级），没有与技术栈目录结构对齐的层级规则。

### 问题3：无自动化验证机制 🔴 严重

**现象**：规范漂移、链接断裂、版本冲突全部靠人工发现

**实证**：
- SW-2026-005工具已有 `naming_checker.py`、`timer_checker.py` 等代码检查器
- 但**没有任何工具**检查规范文件本身的一致性
- `00_INDEX_全局规范索引_V2.0.0.md` 是手工维护的，与实际文件可能不同步
- Obsidian链接完整性无自动检查

**根因**：验证只覆盖了"代码是否符合规范"，没有覆盖"规范本身是否健康"。

### 问题4：.trae 临时文件无限堆积 🟡 中等

**现象**：`.trae/documents/` 和 `.trae/specs/` 大量历史文件堆积

**实证**：
- `.trae/documents/` 有 **40+** 计划文件，多数是一次性执行完毕的
- `.trae/specs/` 有 **20+** spec目录，多数已完成
- `0100_PLC自动化/DJ-2026-005/.trae/documents/` 有 **30+** 计划文件
- 没有清理机制，文件只增不减

**根因**：.trae临时文件没有生命周期管理（创建→使用→归档→清理）。

### 问题5：规范索引手工维护，不可靠 🟡 中等

**现象**：INDEX文件和README与实际文件状态可能不一致

**实证**：
- `00_INDEX_全局规范索引_V2.0.0.md` 声称有38个活跃文件，但这是手写数字
- `01_Project自动化项目管理/00_通用规范/README.md` 没有列出 `215_Python接口文档模板`
- 每次增删规范文件都需要手动更新多个索引文件

**根因**：索引是"文档"而非"数据"，无法自动化生成和验证。

### 问题6：规范归属判断缺乏明确标准 🟡 中等

**现象**：新规范不知道该放哪里

**实证**：
- `908_Siemens_Language_Support_使用指南.md` 在 `0100_PLC自动化/00_通用规范/PLC编程/`，但它是工具使用指南，不是编程规范
- `902_Git使用指南.md` 在 `0100_PLC自动化/00_通用规范/项目管理/`，但Git是跨域工具
- V2.0方案提出过"02_跨域通用规范"但从未创建

**根因**：分类标准不够精确，边界情况没有裁决机制。

---

## 二、根治方案：5层架构

### 核心理念：从"复制分发"到"注册引用"

```
当前模式（复制分发）:
  全局仓库 ──复制──→ PLC目录 ──复制──→ 项目目录
  问题：3个副本独立演化，版本漂移

目标模式（注册引用）:
  规范注册表（唯一真相源）──引用──→ 各使用点
  优势：1个规范只有1个权威位置，其他位置都是指针
```

### 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 5: 人工浏览层                        │
│  Obsidian Vault (00_Obsidian_Base)                          │
│  - INDEX自动生成（从注册表）                                   │
│  - 规范文件通过符号链接/快捷方式引用                            │
└──────────────────────────┬──────────────────────────────────┘
                           │ 自动生成
┌──────────────────────────▼──────────────────────────────────┐
│                    Layer 4: AI感知层                          │
│  .trae/rules/ 层级体系                                       │
│  - workspace级: 通用规则                                     │
│  - tech-stack级: 技术栈规则（引用注册表中的规范路径）            │
│  - project级: 项目特化规则                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ 引用
┌──────────────────────────▼──────────────────────────────────┐
│                    Layer 3: 验证层                            │
│  spec_health_checker.py（SW-2026-005工具扩展）                │
│  - 副本漂移检测                                               │
│  - 版本一致性校验                                             │
│  - 链接完整性检查                                             │
│  - 索引与实际文件一致性                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ 读写
┌──────────────────────────▼──────────────────────────────────┐
│                    Layer 2: 注册层                            │
│  spec_registry.json（规范注册表）                             │
│  - 每个规范ID → 权威位置 + 版本 + 状态                        │
│  - 机器可读，自动生成索引和规则                                │
└──────────────────────────┬──────────────────────────────────┘
                           │ 描述
┌──────────────────────────▼──────────────────────────────────┐
│                    Layer 1: 存储层                            │
│  规范文件物理存储                                             │
│  - 全局PM规范: 00_Obsidian_Base/01_项目管理域/                │
│  - PLC规范: 0100_PLC自动化/00_通用规范/PLC编程/               │
│  - Python规范: 01_Project/00_通用规范/Python开发/             │
│  - 跨域工具: 00_Obsidian_Base/02_跨域通用规范/ (新建)         │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、详细实施方案

### Phase 1：建立规范注册表（Layer 2）

**目标**：创建机器可读的规范注册表，作为唯一真相源

**产出物**：`00_Obsidian_Base全局规范文件仓库/spec_registry.json`

**注册表结构**：
```json
{
  "version": "1.0.0",
  "last_updated": "2026-05-24",
  "specs": {
    "RULE-001": {
      "title": "通用项目名称命名规范",
      "canonical_path": "00_Obsidian_Base全局规范文件仓库/01_项目管理域/00_元规则与治理/001_通用项目名称命名规范_DEV-V1.0.2.md",
      "version": "V1.0.2",
      "domain": "pm",
      "lifecycle": "stable",
      "tags": ["命名", "元规则"],
      "replaces": [],
      "replaced_by": []
    },
    "LSP-905": {
      "title": "SCL编程规范",
      "canonical_path": "0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范.md",
      "version": "V1.0.1",
      "domain": "plc",
      "lifecycle": "stable",
      "tags": ["SCL", "编程", "核心规范"],
      "replaces": ["DEV-801", "DEV-810"],
      "replaced_by": []
    },
    "DEV-801": {
      "title": "PLC变量命名与功能块命名规范",
      "canonical_path": "00_Obsidian_Base全局规范文件仓库/_archive/deprecated/801_PLC变量命名与功能块命名规范_DEV-V1.0.5.md",
      "version": "V1.0.5",
      "domain": "plc",
      "lifecycle": "deprecated",
      "tags": ["命名", "PLC"],
      "replaces": [],
      "replaced_by": ["LSP-905"]
    }
  }
}
```

**关键字段说明**：
- `canonical_path`：规范文件的**唯一权威位置**（相对于工作空间根目录）
- `domain`：归属域（`pm` / `plc` / `python` / `cross-domain`）
- `lifecycle`：生命周期状态（`draft` / `stable` / `deprecated` / `archived`）
- `replaces` / `replaced_by`：替代关系，解决801被905替代这类问题

**执行步骤**：
1. 扫描三个规范目录，收集所有规范文件
2. 为每个文件提取ID、版本、标题
3. 建立替代关系（如801→905）
4. 生成 `spec_registry.json`

---

### Phase 2：创建 .trae/rules 层级体系（Layer 4）

**目标**：让AI助手在不同技术栈项目中自动感知对应规范

**当前问题**：
```
.trae/rules/          ← 仅workspace级，3个文件
  Claude.md           ← 通用规则
  git-commit-message.md
  project-rule.md     ← 混合了PLC和通用规则
```

**目标结构**：
```
.trae/rules/
  Claude.md                    ← workspace级通用规则（精简）
  git-commit-message.md        ← workspace级Git规则（不变）
  project-rule.md              ← workspace级通用规则（移除PLC特定内容）

0100_PLC自动化/.trae/rules/
  plc-rules.md                 ← PLC技术栈规则
  ├── 引用spec_registry中PLC域规范的路径
  ├── Siemens LSP特定规则（从project-rule.md迁移）
  ├── .plc.json配置规则
  └── SCL编码规范要点摘要

01_Project自动化项目管理/.trae/rules/
  python-rules.md              ← Python技术栈规则
  ├── 引用spec_registry中Python域规范的路径
  ├── Python编码规范要点摘要
  └── Qt/FastAPI特定规则
```

**plc-rules.md 内容框架**：
```markdown
---
alwaysApply: true
---

# PLC自动化技术栈规则

## 规范位置
- PLC编程规范权威目录: 0100_PLC自动化/00_通用规范/PLC编程/
- 核心规范: 905_SCL编程规范.md (主规范)
- 配置规范: 907_项目配置规范.md
- 注释规范: 904_SCL注释规范.md
- 定时器规范: 903_定时器使用规范.md
- 错误预防: 906_错误预防规则.md

## 关键规则
1. Siemens LSP的.plc.json中，库引用字段名必须是`libraries`
2. 引用外部共享库时使用相对路径指向库根目录
3. 变量命名采用小驼峰风格（905规范§3）
4. FB_TON定时器PT/ET参数类型为DINT（903规范）
5. 注释禁止中文标点（904规范）
...
```

**执行步骤**：
1. 从 `project-rule.md` 提取PLC特定规则
2. 创建 `0100_PLC自动化/.trae/rules/plc-rules.md`
3. 创建 `01_Project自动化项目管理/.trae/rules/python-rules.md`
4. 精简 `project-rule.md`，仅保留通用规则
5. 验证AI助手在PLC项目中能自动加载plc-rules.md

---

### Phase 3：构建规范健康检查工具（Layer 3）

**目标**：自动化检测规范漂移、版本冲突、索引不一致

**方案**：扩展 SW-2026-005 工具，新增 `spec_health_checker.py`

**检查项**：

| 检查ID | 检查内容 | 严重级别 |
|--------|----------|----------|
| SHC-001 | 同一规范ID在多个位置存在活跃副本 | 🔴 错误 |
| SHC-002 | 规范文件版本与注册表记录不一致 | 🔴 错误 |
| SHC-003 | deprecated规范仍被其他文件引用 | 🟡 警告 |
| SHC-004 | INDEX中列出的文件实际不存在 | 🔴 错误 |
| SHC-005 | 实际存在的规范未在INDEX中列出 | 🟡 警告 |
| SHC-006 | Obsidian [[链接]]指向不存在的文件 | 🟡 警告 |
| SHC-007 | 规范文件缺少必要frontmatter | 🟢 提示 |
| SHC-008 | .trae/rules中引用的规范路径无效 | 🔴 错误 |

**执行方式**：
```bash
# 手动运行
python -m src.checkers.spec_health_checker --workspace "c:\Users\fubai\Desktop\My_Workspace"

# 输出报告
# SHC-001 [ERROR] 规范DEV-801在3个位置存在活跃副本:
#   - 0100_PLC自动化/DJ-2026-005/.../801_..._V1.0.7.md (V1.0.7)
#   - 00_Obsidian_Base/_archive/deprecated/801_..._V1.0.5.md (V1.0.5, deprecated)
#   建议: 项目级副本应替换为对canonical_path的引用
```

**执行步骤**：
1. 在 SW-2026-005 的 `src/checkers/` 下新建 `spec_health_checker.py`
2. 实现SHC-001到SHC-008共8个检查项
3. 集成到现有checker框架（`rule_registry.py`）
4. 编写测试用例
5. 运行检查并修复发现的问题

---

### Phase 4：规范生命周期管理

**目标**：每个规范有明确的状态，状态转换有规则

**生命周期状态机**：
```
  draft ──审核通过──→ stable ──有替代──→ deprecated ──归档──→ archived
    │                   │                                      │
    └──废弃──→ archived └──重大修订──→ draft(新版本)            └──永久保留
```

**规范文件frontmatter标准**：
```markdown
---
spec_id: LSP-905
title: SCL编程规范
version: V1.0.1
domain: plc
lifecycle: stable
canonical_path: 0100_PLC自动化/00_通用规范/PLC编程/905_SCL编程规范.md
replaces: [DEV-801, DEV-810]
replaced_by: []
last_updated: 2026-05-04
---
```

**状态转换规则**：
| 转换 | 触发条件 | 必须操作 |
|------|----------|----------|
| draft → stable | 审核通过 + 至少1个项目验证 | 更新注册表 |
| stable → deprecated | 有新规范替代 | 在文件头部添加废弃声明 + 重定向 |
| deprecated → archived | 超过3个月无引用 | 移入 `_archive/` + 更新注册表 |
| stable → draft(新版本) | 需要重大修订 | 旧版标记为deprecated |

**执行步骤**：
1. 为所有活跃规范文件添加frontmatter
2. 在 `spec_registry.json` 中记录lifecycle状态
3. 建立deprecated规范的重定向机制（文件头部声明替代关系）

---

### Phase 5：索引自动生成与Obsidian桥接（Layer 5）

**目标**：INDEX文件从注册表自动生成，消除手工维护的不一致

**方案**：编写 `generate_index.py` 脚本

**输入**：`spec_registry.json`
**输出**：
- `00_INDEX_全局规范索引_V2.0.0.md`（自动生成，带生成时间戳）
- `0100_PLC自动化/00_通用规范/README.md`（自动生成）
- `01_Project自动化项目管理/00_通用规范/README.md`（自动生成）

**生成逻辑**：
```python
def generate_index(registry, domain_filter=None):
    """从注册表生成Markdown索引"""
    specs = [s for s in registry["specs"].values()
             if domain_filter is None or s["domain"] == domain_filter]
    # 按domain → lifecycle → 编号排序
    # 生成表格、引用关系图、快速查找指南
    # 添加自动生成标记: "⚠️ 本文件由spec_registry.json自动生成，请勿手动编辑"
```

**Obsidian兼容性**：
- 生成的INDEX使用Obsidian `[[链接]]` 格式
- 规范文件通过Obsidian的"快捷方式"（.url文件）实现跨vault引用
- 或者：将 `00_Obsidian_Base` 的Obsidian vault范围扩展到包含整个工作空间

**执行步骤**：
1. 编写 `generate_index.py`
2. 从 `spec_registry.json` 生成三个INDEX文件
3. 在INDEX文件头部添加自动生成标记
4. 设置定期运行（可手动触发或git hook触发）

---

### Phase 6：清理现有问题

**目标**：修复当前已知的所有规范管理问题

**具体清理项**：

| # | 问题 | 修复操作 |
|---|------|----------|
| C1 | DJ-2026-005项目中的801规范(V1.0.7)与归档版本(V1.0.5)漂移 | 确认V1.0.7为权威版本，更新注册表，项目级文件添加canonical_path引用 |
| C2 | `215_Python接口文档模板` 未在Python README索引中列出 | 更新README（或由自动生成解决） |
| C3 | `908_Siemens_Language_Support_使用指南` 归类不当（应在工具链而非PLC编程） | 移至 `0100_PLC自动化/00_通用规范/工具链/` 或重新分类 |
| C4 | `902_Git使用指南` 在PLC目录下，但Git是跨域工具 | 移至 `00_Obsidian_Base/02_跨域通用规范/` |
| C5 | .trae/documents 40+历史计划文件堆积 | 已完成的计划移入 `_archive/documents/` |
| C6 | .trae/specs 20+已完成spec目录堆积 | 已完成的spec移入 `_archive/specs/` |
| C7 | `project-rule.md` 中PLC规则与通用规则混合 | 拆分到 `plc-rules.md` |

---

## 四、实施优先级与依赖关系

```
Phase 1 (注册表) ────────────────────────────── 基础，必须先做
    │
    ├──→ Phase 4 (生命周期) ──→ Phase 5 (索引自动生成)
    │
    ├──→ Phase 3 (健康检查) ──→ Phase 6 (清理现有问题)
    │
    └──→ Phase 2 (.trae层级) ──→ Phase 6 (清理现有问题)
```

**推荐执行顺序**：
1. **Phase 1**（注册表）— 1-2天，所有其他Phase的基础
2. **Phase 2**（.trae层级）— 0.5天，立竿见影改善AI助手体验
3. **Phase 4**（生命周期）— 1天，为规范添加frontmatter
4. **Phase 3**（健康检查）— 2天，需要开发Python工具
5. **Phase 5**（索引自动生成）— 1天，依赖注册表数据完整
6. **Phase 6**（清理）— 1天，依赖健康检查工具就绪

---

## 五、长期维护规则

### 5.1 新增规范时的标准流程

```
1. 判断归属域:
   - 与技术栈相关? → 放入对应技术栈的00_通用规范/
   - 与技术栈无关? → 放入00_Obsidian_Base/01_项目管理域/ 或 02_跨域通用规范/

2. 创建规范文件（含frontmatter）:
   spec_id, version, domain, lifecycle=draft

3. 更新spec_registry.json:
   添加新条目

4. 运行 generate_index.py:
   自动更新所有INDEX文件

5. 运行 spec_health_checker.py:
   验证无冲突
```

### 5.2 规范修改时的标准流程

```
1. 修改canonical_path处的规范文件
2. 更新frontmatter中的version和last_updated
3. 更新spec_registry.json中的版本号
4. 运行 generate_index.py 更新索引
5. 运行 spec_health_checker.py 验证
```

### 5.3 定期维护（建议每月1次）

```
1. 运行 spec_health_checker.py 全量检查
2. 检查deprecated规范是否可以归档
3. 清理.trae/documents和.trae/specs中的已完成项
4. 验证.trae/rules引用的规范路径仍然有效
```

---

## 六、预期收益

| 维度 | 当前状态 | 方案落地后 | 改善 |
|------|----------|-----------|------|
| **版本漂移** | 801规范3个副本3个版本 | 1个权威位置+注册表引用 | ✅ 根除 |
| **AI感知** | AI不知道905规范存在 | .trae/rules自动加载技术栈规范 | ✅ 根除 |
| **索引可靠性** | 手工维护，可能过时 | 自动生成，与注册表同步 | ✅ 根除 |
| **问题发现** | 靠人工偶然发现 | 自动化健康检查 | ✅ 根除 |
| **.trae堆积** | 40+文件无限增长 | 生命周期管理+定期清理 | ✅ 根除 |
| **规范归属** | 边界模糊，凭感觉 | 注册表domain字段精确分类 | ✅ 根除 |
| **维护成本** | 每次变更需手动更新3-4处 | 修改1处+运行脚本 | ⬇️ 70% |

---

## 七、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 注册表与实际文件不同步 | 中 | 高 | spec_health_checker定期校验 |
| .trae/rules层级不被Trae IDE识别 | 低 | 高 | 先验证Trae是否支持子目录rules，不支持则用workspace级rules引用 |
| Obsidian无法跨vault链接 | 中 | 中 | 扩展vault范围或使用.url快捷方式 |
| frontmatter增加维护负担 | 低 | 低 | 由generate_index.py自动提取，无需手写 |
| 团队成员不遵守新流程 | 中 | 中 | spec_health_checker作为门禁，不通过不允许提交 |

---

*方案编制: 2026-05-24 | 状态: 待审核*
