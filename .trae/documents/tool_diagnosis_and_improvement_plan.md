# Python项目管理工具V2.4.0 问题诊断与迭代改进计划

## 一、问题发现

基于对 `DJ-2026-001_buffer_framing_machine（边框缓存机）` 项目的深度检查，发现以下问题：

### 🔴 问题1：{project_code}占位符未被替换（严重Bug）

**影响范围**：15个文件

| 序号 | 文件路径 | 当前错误名称 | 应有名称 |
|:----:|---------|-------------|---------|
| 1 | `00_项目管理/01_立项与需求/` | `{project_code}_项目立项表.md` | `DJ-2026-001_项目立项表.md` |
| 2 | `00_项目管理/01_立项与需求/` | `{project_code}_需求分析文档.md` | `DJ-2026-001_需求分析文档.md` |
| 3 | `10_技术设计/11_Eplan电气/Source/` | `{project_code}_PLC硬件配置表.md` | `DJ-2026-001_PLC硬件配置表.md` |
| 4 | `10_技术设计/11_Eplan电气/Export_PDF/` | `{project_code}_电气图纸清单.md` | `DJ-2026-001_电气图纸清单.md` |
| 5 | `10_技术设计/12_机械结构/3D_Models/` | `{project_code}_机械BOM清单.md` | `DJ-2026-001_机械BOM清单.md` |
| 6 | `20_软件程序/21_PLC_Autoshop/Docs/` | `{project_code}_IO分配表.md` | `DJ-2026-001_IO分配表.md` |
| 7 | `20_软件程序/21_PLC_Autoshop/Docs/` | `{project_code}_PLC程序设计总文档.md` | `DJ-2026-001_PLC程序设计总文档.md` |
| 8 | `20_软件程序/21_PLC_Autoshop/Docs/` | `{project_code}_系统架构设计说明书.md` | `DJ-2026-001_系统架构设计说明书.md` |
| 9 | `20_软件程序/21_PLC_Autoshop/Docs/` | `{project_code}_联锁逻辑设计说明书.md` | `DJ-2026-001_联锁逻辑设计说明书.md` |
| 10 | `40_交付与文档/41_操作手册/` | `{project_code}_操作手册.md` | `DJ-2026-001_操作手册.md` |
| 11 | `40_交付与文档/43_验收清单/` | `{project_code}_验收检查表.md` | `DJ-2026-001_验收检查表.md` |
| 12 | `40_交付与文档/44_培训资料/` | `{project_code}_培训记录.md` | `DJ-2026-001_培训记录.md` |
| 13 | `40_交付与文档/45_故障排查指南/` | `{project_code}_故障排除手册.md` | `DJ-2026-001_故障排除手册.md` |
| 14 | `40_交付与文档/46_维护计划/` | `{project_code}_维护手册.md` | `DJ-2026-001_维护手册.md` |
| 15 | `40_交付与文档/...` | （可能还有其他） | ... |

**根因分析**：
- 模板文件中使用`{project_code}`作为占位符
- 项目创建时工具的变量替换逻辑未正确执行
- 可能是字符串替换函数遗漏或正则表达式匹配问题

### 🟠 问题2：变更管理目录结构不完整（规范符合性）

**当前工具生成**：
```
04_变更管理/
└── 01_变更单/
    ├── CHG-DOCU/     ✅
    ├── CHG-PLC/      ✅
    └── CHG-SCPT/     ✅
```

**Obsidian规范要求（043_通用变更管理目录结构说明_PM-V2.1.0）**：
```
04_变更管理/
├── 01_变更单/
│   ├── CHG-ELEC/     ❌ 缺失（电气设计类）
│   ├── CHG-MECH/     ❌ 缺失（机械结构类）
│   ├── CHG-PLC/      ✅ 已有
│   ├── CHG-HMI/      ❌ 缺失（HMI程序类）
│   ├── CHG-SCPT/     ✅ 已有
│   ├── CHG-DOCU/     ✅ 已有
│   └── CHG-SAFE/     ❌ 缺失（安全功能类）
├── [项目编号]_版本变更台帐.md  ❌ 缺失
└── README.md                ❌ 缺失（根目录说明）
```

**差异统计**：
- 缺少4个变更类型子目录：ELEC、MECH、HMI、SAFE
- 缺少版本变更台帐文件
- 缺少根目录README.md

### 🟡 问题3：文档内容为空模板（功能缺失）

**现状**：
- 工具生成的文档只有标题和章节框架
- 实际内容需要手动填充或AI辅助生成
- 部分文档（如机械BOM清单）只有4行空标题

**期望**：
- 至少基于项目基本信息自动填充基础内容
- 或提供"一键填充"功能调用AI生成

---

## 二、问题定性

### 2.1 是模板问题还是工具问题？

| 问题 | 定性 | 原因 |
|------|:----:|------|
| **{project_code}未替换** | **工具Bug** | 模板定义正确，但执行替换时失败 |
| **变更目录不完整** | **模板缺陷** | TPL-SINGLE-PLC-001模板定义的目录不完整 |
| **文档内容空白** | **功能缺失** | 工具缺少"文档自动填充"功能 |

### 2.2 是否需要迭代工具？

**结论：必须迭代，具体分为3个优先级**

| 优先级 | 迭代内容 | 工作量 | 影响 |
|:------:|---------|:-----:|:----:|
| **P0 紧急** | 修复{project_code}替换Bug | 小（1-2小时） | 影响所有新建项目 |
| **P1 重要** | 更新TPL-SINGLE-PLC-001模板 | 中（半天） | 符合Obsidian规范V2.1.0 |
| **P2 增强** | 增加"文档智能填充"功能 | 大（需规划） | 提升用户体验 |

---

## 三、实施计划

### Phase 1：紧急修复（P0）- 1-2小时

#### 步骤1.1：定位Bug代码

**检查位置**：
```python
# 可能在以下文件中：
src/services/project_service.py    # 项目创建服务
src/utils/template_utils.py        # 模板处理工具
src/core/template_manager.py        # 模板管理器
config/templates/TPL-SINGLE-PLC-001/ # 模板定义文件
```

**关键函数**：
```python
# 查找类似这样的代码
def replace_template_variables(template_path, project_code):
    # 这里可能有bug
    content = read_file(template_path)
    content.replace("{project_code}", project_code)  # ← 检查这里
```

#### 步骤1.2：修复并验证

**修复方案**：
```python
# 方案A：递归替换所有文件名
def rename_template_files(root_dir, project_code):
    for file in Path(root_dir).rglob("*project_code*"):
        new_name = file.name.replace("{project_code}", project_code)
        file.rename(file.parent / new_name)

# 方案B：在项目创建后统一处理
def post_create_project(project_path, project_code):
    # 创建完成后扫描并重命名
    scan_and_rename_files(project_path, project_code)
```

**验证方法**：
1. 删除现有测试项目
2. 使用工具重新创建项目
3. 检查所有文件名是否正确替换
4. 回归测试：创建不同业务线项目（SW/DJ/ZD）

---

### Phase 2：模板更新（P1）- 半天

#### 步骤2.1：更新变更管理目录结构

**修改文件**：`TPL-SINGLE-PLC-001` 模板定义

**添加缺失目录**：
```
04_变更管理/
└── 01_变更单/
    ├── CHG-ELEC/          # 新增
    │   └── README.md     # 新增
    ├── CHG-MECH/          # 新增
    │   └── README.md     # 新增
    ├── CHG-PLC/           # 已有
    │   └── README.md     # 已有
    ├── CHG-HMI/           # 新增
    │   └── README.md     # 新增
    ├── CHG-SCPT/          # 已有
    │   └── README.md     # 已有
    ├── CHG-DOCU/          # 已有
    │   └── README.md     # 已有
    ├── CHG-SAFE/          # 新增
    │   └── README.md     # 新增
    ├── {project_code}_版本变更台帐.md  # 新增
    └── README.md                 # 新增（根目录）
```

#### 步骤2.2：同步其他模板

检查并更新所有模板的变更管理部分：
- TPL-AUTO-LINE-001（自动化整线）
- TPL-DJ-STATION-001（单机设备工站）
- 其他已有模板...

---

### Phase 3：功能增强（P2）- 需单独规划

#### 步骤3.1：增加"文档智能填充"功能

**可选方案**：

**方案A：集成AI填充（推荐）**
- 调用大语言模型API
- 基于项目信息+已迁移文件自动生成内容
- 用户审核确认后保存

**方案B：规则引擎填充**
- 基于IO表.xlsx自动填充IO分配表
- 基于PLC程序结构自动填充程序设计文档
- 基于HMI界面自动生成操作手册大纲

**方案C：向导式引导填充**
- 创建项目后弹出"文档填充向导"
- 分步骤引导用户填写或选择"AI辅助"
- 支持批量填充和单个文档填充

---

## 四、临时解决方案（立即可用）

在工具修复前，可使用脚本批量修复现有项目：

```powershell
# 修复脚本：批量替换{project_code}
param(
    [string]$ProjectPath,
    [string]$ProjectCode = "DJ-2026-001"
)

Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object {
    $_.Name -like "*project_code*"
} | ForEach-Object {
    $newName = $_.Name.Replace("{project_code}", $ProjectCode)
    Rename-Item -Path $_.FullName -NewName $newName
    Write-Host "✅ 重命名: $($_.Name) → $newName"
}

Write-Host "`n完成！共处理了 $((Get-ChildItem -Path $ProjectPath -Recurse -File | Where-Object { $_.Name -like '*project_code*' }).Count) 个文件"
```

**使用方法**：
```powershell
.\fix_project_names.ps1 -ProjectPath "D:\...\DJ-2026-001_buffer_framing_machine（边框缓存机）"
```

---

## 五、后续建议

### 5.1 立即行动项

- [ ] **今天**：运行修复脚本修正当前项目的15个文件名
- [ ] **本周**：定位并修复{project_code}替换Bug（P0）
- [ ] **下周**：更新TPL-SINGLE-PLC-001模板（P1）

### 5.2 中期改进项

- [ ] **本月**：审查所有模板的规范符合性
- [ ] **下月**：规划设计"文档智能填充"功能（P2）
- [ ] **持续**：建立模板版本管理机制

### 5.3 长期优化方向

1. **模板验证机制**：创建项目前自动检查模板完整性
2. **规范同步工具**：当Obsidian规范更新时，自动提示模板需要更新
3. **用户反馈收集**：在工具中集成"问题报告"功能
4. **自动化测试**：为模板和工具功能编写单元测试和集成测试

---

## 六、完整迭代与发布流程

### 6.1 迭代周期概览

```
问题发现 → Bug修复 → 模板更新 → 测试验证 → 文档同步 → 版本打包 → 发布交付
   (已完成)   (P0)      (P1)      (验证)    (同步)     (打包)    (交付)
```

### 6.2 Phase 0：当前项目修复（立即可用）

**目标**：修复已创建的DJ-2026-001项目的15个文件名问题

**方法**：使用批量重命名脚本（见第四章）

### 6.3 Phase 1：工具Bug修复（P0）- 预计1-2小时

**修改文件**：
- `src/services/project_service.py` - 项目创建服务
- 或 `src/utils/template_utils.py` - 模板工具函数

**修复内容**：
```python
# 在项目创建完成后添加
def post_process_project(project_path: str, project_code: str):
    """项目创建后处理：替换模板占位符"""
    import os
    from pathlib import Path
    
    for file in Path(project_path).rglob("*"):
        if "{project_code}" in file.name:
            new_name = file.name.replace("{project_code}", project_code)
            file.rename(file.parent / new_name)
    
    # 同时处理文件内容中的占位符
    for file in Path(project_path).rglob("*.md"):
        content = file.read_text(encoding="utf-8")
        if "{project_code}" in content:
            content = content.replace("{project_code}", project_code)
            file.write_text(content, encoding="utf-8")
```

**版本号更新**：
- 当前版本：V2.4.0
- 修复后版本：**V2.4.1**

### 6.4 Phase 2：模板规范更新（P1）- 预计半天

**修改内容**：

#### 6.4.1 更新TPL-SINGLE-PLC-001模板

**变更管理目录补全**：
```
新增目录：
├── CHG-ELEC/           # 电气设计类变更
├── CHG-MECH/           # 机械结构类变更  
├── CHG-HMI/            # HMI程序类变更
├── CHG-SAFE/           # 安全功能类变更
├── {project_code}_版本变更台帐.md
└── README.md           # 变更管理根目录说明
```

**README.md内容示例**（CHG-PLC）：
```markdown
# PLC程序类变更单

## 用途
存放所有PLC程序相关的变更记录和文档。

## 命名规范
- 变更单文件：`CHG-PLC-[YYYY]-[序号].md`
- 示例：`CHG-PLC-2026-001_边框缓存机取料逻辑优化.md`

## 典型变更类型
- 程序逻辑修改
- IO点位调整
- 功能块(FB)新增或修改
- 通讯协议变更

## 关联文档
- [IO分配表](../../20_软件程序/21_PLC_Autoshop/Docs/{project_code}_IO分配表.md)
- [PLC程序设计总文档](../../20_软件程序/21_PLC_Autoshop/Docs/{project_code}_PLC程序设计总文档.md)
```

#### 6.4.2 同步检查其他模板

需检查的模板清单：
- [ ] TPL-SINGLE-PLC-001（本次重点）
- [ ] TPL-AUTO-LINE-001（自动化整线）
- [ ] TPL-DJ-STATION-001（单机设备工站）
- [ ] 其他已有模板...

**版本号更新**：
- 模板修复后版本：**V2.5.0**（主版本升级，因结构变更）

### 6.5 Phase 3：测试验证 - 预计2小时

#### 6.5.1 单元测试

**测试用例**：
| 编号 | 测试项 | 验证方法 | 预期结果 |
|:----:|-------|---------|---------|
| T-001 | 项目创建后无{project_code}文件 | 创建测试项目，扫描文件名 | ✅ 全部替换 |
| T-002 | 文档内容中无{project_code} | 检查.md文件内容 | ✅ 全部替换 |
| T-003 | 变更管理目录完整 | 检查04_变更管理/结构 | ✅ 7个子目录+台帐+README |
| T-004 | 不同业务线项目正常 | 创建SW/DJ/ZD项目 | ✅ 各自正确 |

#### 6.5.2 回归测试

**必测场景**：
1. 创建新的DJ项目（单机设备）
2. 创建新的ZD项目（自动化整线）
3. 使用不同模板创建项目
4. 导入历史项目（如有此功能）

### 6.6 Phase 4：项目文档同步 - 预计1小时

**同步内容**：

#### 6.6.1 工具使用文档更新

需更新的文档：
- [ ] `07_技术知识库/04_开发规范/` - 补充已知问题和解决方案
- [ ] `00_项目管理/05_模板结构说明.md` - 更新为V2.5.0模板结构
- [ ] README.md - 更新版本号和变更日志

#### 6.6.2 规范文件同步

需同步到Obsidian全局规范仓库的内容：
- [ ] 新增/更新模板缺陷记录
- [ ] 最佳实践案例（基于本次迁移经验）

### 6.7 Phase 5：版本打包与交付物准备 - 预计1小时

#### 6.7.1 版本号规划

| 版本 | 类型 | 内容 | 发布时间 |
|:----:|:----:|-----|:--------:|
| **V2.4.1** | 补丁版 | 仅修复{project_code}Bug | 本周内 |
| **V2.5.0** | 次版本 | 模板结构更新+规范对齐 | 下周 |

#### 6.7.2 V2.4.1 打包清单（紧急修复版）

**必须包含**：
```
Python自动化项目管理系统_V2.4.1_YYYYMMDD/
├── 01_可执行文件/
│   ├── Python项目管理工具.exe          # 主程序
│   ├── config/                         # 配置文件
│   └── src/plugins/                    # 插件
├── 02_发布说明/
│   ├── V2.4.1_更新说明.md              # 本次修复内容
│   ├── V2.4.1_已知问题.md              # 已知限制
│   └── V2.4.1_使用指南.md              # 快速上手
└── 03_测试报告/
    └── V2.4.1_测试报告.md              # 测试结果
```

**V2.4.1_更新说明.md 内容**：
```markdown
# Python项目管理工具 V2.4.1 更新说明

## 发布日期：2026-04-15
## 版本类型：补丁修复（Patch Release）

---

## 修复内容

### 🔧 Bug修复
- **[FIX-001] 严重**：修复新建项目时{project_code}占位符未被替换的问题
  - 影响：所有新建项目的15个文档文件名包含未替换的占位符
  - 修复：优化模板变量替换逻辑，支持文件名和内容双重替换
  - 验证：已通过3个不同业务线项目的回归测试

### 📝 文档更新
- 更新《用户操作手册》相关章节
- 补充《常见问题解答》FAQ

---

## 安装说明

1. 解压到任意目录
2. 双击 `Python项目管理工具.exe` 启动
3. 已有项目无需特殊处理（仅影响新建项目）

## 已知问题

- [ ] 模板变更管理目录不完全符合Obsidian规范V2.1.0（计划在V2.5.0解决）
- [ ] 文档自动填充功能尚未实现（规划中）

## 反馈渠道

如遇问题请联系：[联系方式]
```

#### 6.7.3 V2.5.0 打包清单（模板更新版）

**额外包含**：
```
├── config/templates/
│   └── TPL-SINGLE-PLC-001/             # 更新的单机设备模板
│       ├── 04_变更管理/                 # 完整的变更管理结构
│       │   ├── 01_变更单/
│       │   │   ├── CHG-ELEC/...        # 新增
│       │   │   ├── CHG-MECH/...        # 新增
│       │   │   ├── CHG-HMI/...         # 新增
│       │   │   ├── CHG-SAFE/...        # 新增
│       │   │   └── {project_code}_版本变更台帐.md  # 新增
│       │   └── README.md               # 新增
│       └── ...
├── 02_发布说明/
│   ├── V2.5.0_更新说明.md              # 模板重大更新
│   └── V2.5.0_迁移指南.md              # 从旧版本迁移指南
└── 03_测试报告/
    └── V2.5.0_规范符合性报告.md         # 与Obsidian规范对比
```

### 6.8 Phase 6：发布交付

#### 6.8.1 内部发布流程

```
代码完成 → 单元测试 → 集成测试 → 打包 → 内部验收 → 正式发布
  ↓           ↓          ↓          ↓         ↓          ↓
  完成      通过       通过       完成      通过      发布
```

#### 6.8.2 交付物清单

**交付给用户**：
1. ✅ 可执行程序包（.zip/.exe安装包）
2. ✅ 更新说明文档
3. ✅ 版本变更日志
4. ✅ 快速入门指南（可选）

**归档留存**：
1. 源代码备份（Git Tag标记）
2. 测试报告存档
3. 用户反馈记录

---

## 七、时间估算汇总

| 阶段 | 任务 | 时间 | 负责人 |
|:----:|-----|:----:|:------:|
| 0 | 当前项目修复 | 10分钟 | 用户自行/脚本 |
| 1 | Bug修复(P0) | 1-2小时 | 开发工程师 |
| 2 | 模板更新(P1) | 半天 | 开发工程师 |
| 3 | 测试验证 | 2小时 | 测试/QA |
| 4 | 文档同步 | 1小时 | 技术文档 |
| 5 | 打包准备 | 1小时 | 发布工程师 |
| **总计** | **完整迭代** | **约2个工作日** | - |

**快速通道（仅修Bug）**：1天内的紧急修复版V2.4.1
**完整迭代（含模板更新）**：3-5工作日的正式版V2.5.0