# 多项目共用SysLib库管理方案（修订版）

## 📋 方案概述

**目标**: 在 Siemens LSP 插件环境下，实现多个PLC项目共用一个SysLib库，且不发生类型冲突

**核心原则**:
- 使用 `.plc.json` 的 `libraries` 字段引用共享库
- 每个项目保持独立的类型作用域
- 符合 Dynamic Siemens Language Support 插件规范
- **所有项目统一在 `0100_项目` 目录下管理**

---

## 🔍 当前状态分析

### 现有结构（迁移前）
```
d:\BaiduSyncdisk\My_Workspace\
├── DJ-2026-005\              # ❌ 项目在根目录
│   ├── .plc.json             # libraries: []
│   ├── SysLib\               # ❌ 库在项目内部
│   ├── OB1\
│   ├── DB1\
│   └── FB100\
│
├── 0100_项目\                # ✅ 目标目录（已存在）
    └── DJ-2026-005_边框缓存机\  # ✅ 项目文档在此
        └── ...
```

### 存在的问题
1. **项目分散**: PLC源码和项目文档分离在不同位置
2. **库耦合**: SysLib 嵌套在 DJ-2026-005 内部，其他项目无法使用
3. **重复维护**: 每个项目可能需要复制一份 SysLib
4. **版本不一致**: 多份副本可能导致版本差异

---

## ✅ 推荐方案：统一迁移到 0100_项目 + 独立共享库

### 1️⃣ 目标目录结构

```
d:\BaiduSyncdisk\My_Workspace\0100_项目\
│
├── 01_SharedLibraries\                    # 📦 新建：共享库根目录
│   └── SysLib\                            # 共享的SysLib库
│       ├── README.md
│       ├── timer\
│       │   ├── FB_TON.scl
│       │   ├── FB_TOF.scl
│       │   ├── FB_TONR.scl
│       │   └── FB_TP.scl
│       ├── counter\
│       │   ├── FB_CTD.scl
│       │   ├── FB_CTU.scl
│       │   └── FB_CTUD.scl
│       ├── convert\
│       │   ├── FC_DINT_TO_TIME.scl
│       │   ├── FC_INT_TO_TIME.scl
│       │   ├── FC_TIME_TO_DINT.scl
│       │   └── FC_TIME_TO_INT.scl
│       ├── edge\
│       │   ├── FB_F_TRIG.scl
│       │   └── FB_R_TRIG.scl
│       ├── pulse\
│       │   └── FB_TaktGenerator.scl
│       └── log\
│           └── FC_LogMsg.scl
│
├── DJ-2026-005_边框缓存机\                # 🎯 项目A（从根目录迁入）
│   ├── .plc.json                         # 配置引用共享库
│   ├── 00_项目管理\                       # 已存在的项目文档
│   ├── 01_需求与设计\
│   ├── 02_PLC程序\
│   ├── OB1\                              # 从 DJ-2026-005 迁入
│   ├── DB1\                              # 从 DJ-2026-005 迁入
│   ├── FB100\                            # 从 DJ-2026-005 迁入
│   ├── Test\                             # 从 DJ-2026-005 迁入
│   └── ...                               # 其他PLC源文件
│
└── DJ-2026-XXX_新项目\                    # 🎯 项目B（未来）
    ├── .plc.json                         # 配置引用同一个共享库
    ├── OB1\
    └── ...
```

### 2️⃣ .plc.json 配置示例

#### DJ-2026-005_边框缓存机 项目配置
```json
{
    "name": "DJ-2026-005_边框缓存机",
    "description": "边框缓存机PLC控制项目",
    "version": "1.0.0",
    "libraries": [
        "../01_SharedLibraries/SysLib"
    ]
}
```

#### DJ-2026-XXX_新项目 配置（未来示例）
```json
{
    "name": "DJ-2026-XXX_新项目",
    "description": "第二个PLC项目",
    "version": "1.0.0",
    "libraries": [
        "../01_SharedLibraries/SysLib"
    ]
}
```

---

## 🛡️ 冲突避免机制（基于插件文档）

### 插件保证的隔离性

根据 **Dynamic Siemens Language Support** 官方文档：

> **Type lookups never fall back to other PLC roots; each `.plc.json` keeps its scope isolated.**

✅ **关键保障**:
1. **类型隔离**: 每个项目的类型查找不会泄漏到其他项目
2. **独立作用域**: 每个 `.plc.json` 定义自己的作用域边界
3. **库只读访问**: libraries 作为只读源包含，不会互相干扰

### 工作原理图示

```
d:\BaiduSyncdisk\My_Workspace\0100_项目\
│
├─────────────────────────────────────────────────────┐
│                  VS Code Workspace                   │
│                                                     │
│  ┌────────────────────────┐  ┌────────────────────┐  │
│  │ DJ-2026-005_边框缓存机  │  │ DJ-2026-XXX_新项目  │  │
│  │ ┌──────────────────┐  │  │ ┌────────────────┐  │  │
│  │ │ .plc.json        │  │  │ │ .plc.json      │  │  │
│  │ │ libraries:       │  │  │ │ libraries:     │  │  │
│  │ │  [../SysLib]     │  │  │ │  [../SysLib]   │  │  │
│  │ └────────┬─────────┘  │  │ └────────┬───────┘  │  │
│  │          │            │  │          │           │  │
│  │ ▼ 独立作用域          │  │ ▼ 独立作用域         │  │
│  │ · OB1.scl            │  │ · OB1.scl           │  │
│  │ · DB1.db (GlobalVars)│  │ · DB2.db           │  │
│  │ · FB100\ValveControl │  │ · OtherFBs         │  │
│  └──────────┬───────────┘  └──────────┬──────────┘  │
│             │                          │              │
│             └──────────┬───────────────┘              │
│                        ▼                              │
│             ┌──────────────────────┐                  │
│             │ 01_SharedLibraries   │ ← 只读共享        │
│             │ └── SysLib\         │                  │
│             │     · timer\        │                  │
│             │     · counter\      │                  │
│             │     · convert\      │                  │
│             │     · ...           │                  │
│             └──────────────────────┘                  │
│                        ↑                              │
│              所有项目共同引用（只读）                   │
└─────────────────────────────────────────────────────┘
```

---

## 📝 实施步骤（分阶段执行）

### 阶段1：创建共享库目录结构

#### 步骤1.1：创建共享库根目录
```bash
mkdir "d:\BaiduSyncdisk\My_Workspace\0100_项目\01_SharedLibraries\SysLib"
```

#### 步骤1.2：迁移 SysLib 内容
```
源: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\SysLib\*.*
目标: d:\BaiduSyncdisk\My_Workspace\0100_项目\01_SharedLibraries\SysLib\

操作:
  - 复制 timer\, counter\, convert\, edge\, pulse\, log\ 所有子目录
  - 复制 README.md
```

### 阶段2：迁移 DJ-2026-005 项目到 0100_项目

#### 步骤2.1：迁移PLC源代码目录
```
源目录（从 DJ-2026-005 迁移）:
  - OB1\
  - DB1\
  - FB100\
  - Test\

目标目录:
  d:\BaiduSyncdisk\My_Workspace\0100_项目\DJ-2026-005_边框缓存机\

注意: 
  - 00_项目管理\ 等文档目录已存在于目标位置，无需迁移
  - 只需迁移 PLC 源代码相关目录
```

#### 步骤2.2：在新位置创建 .plc.json
```json
{
    "name": "DJ-2026-005_边框缓存机",
    "description": "边框缓存机PLC控制项目",
    "version": "1.0.0",
    "libraries": [
        "../01_SharedLibraries/SysLib"
    ]
}
```

**文件位置**: `d:\BaiduSyncdisk\My_Workspace\0100_项目\DJ-2026-005_边框缓存机\.plc.json`

### 阶段3：清理旧位置

#### 步骤3.1：删除旧位置的 SysLib
```
删除: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\SysLib\
原因: 已迁移到共享位置
```

#### 步骤3.2：删除旧位置的PLC源码目录
```
删除: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\OB1\
删除: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\DB1\
删除: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\FB100\
删除: d:\BaiduSyncdisk\My_Workspace\DJ-2026-005\Test\
原因: 已迁移到 0100_项目 下
```

#### 步骤3.3：保留或归档旧项目根目录
```
选项A（推荐）: 删除空的 DJ-2026-005 根目录
选项B: 保留为空目录或添加 README 说明已迁移
```

### 阶段4：验证与测试

#### 步骤4.1：触发 LSP 重新扫描
```
操作: 在 VS Code 中打开任意 .scl 文件并保存
目的: 让插件重新读取新的 .plc.json 和 libraries 配置
```

#### 步骤4.2：运行编译检查
```
验证项:
  - [ ] LSP 无诊断错误
  - [ ] 类型补全正常显示 SysLib 中的 FB/FC
  - [ ] 跳转到定义能正确跳转到共享库文件
```

#### 步骤4.3：运行功能测试
```
操作: 运行 valve_test.scltest 测试套件
预期: 所有测试用例通过（与迁移前一致）
```

---

## ⚠️ 注意事项和最佳实践

### 1️⃣ 路径规则（重要！）

根据插件文档：
> **libraries paths are resolved relative to the `.plc.json` file and must exist to be used.**

✅ **当前方案的相对路径关系**:
```
0100_项目/
├── DJ-2026-005_边框缓存机/
│   └── .plc.json              ← 这里是基准点
│       libraries: ["../01_SharedLibraries/SysLib"]
│                    ↑
│                    └回到 0100_项目/ 再进入 01_SharedLibraries/SysLib
│
└── 01_SharedLibraries/
    └── SysLib/                ← 目标位置 ✓
```

❌ **错误示例**:
```json
"libraries": ["./SysLib"]                    // 错误：相对路径不对
"libraries": ["D:/BaiduSyncdisk/..."]        // 可能不支持绝对路径
"libraries": ["../../01_SharedLibraries"]     // 错误：多了一层
```

### 2️⃣ 库的版本管理（建议）

将 `01_SharedLibraries` 纳入版本控制：

```bash
# 如果 0100_项目 已是 Git 仓库
cd "d:\BaiduSyncdisk\My_Workspace\0100_项目"
git add 01_SharedLibraries/
git commit -m "添加SysLib共享库"

# 或作为 Git Submodule（如果需要独立版本管理）
git submodule add https://github.com/your-repo/SysLib.git 01_SharedLibraries/SysLib
```

### 3️⃣ 库的修改规范

由于库被多个项目共享：
- **修改前**: 确认所有依赖项目兼容
- **修改后**: 通知所有项目成员更新
- **版本标记**: 使用 Git tag 记录变更
- **测试验证**: 至少在一个项目中完整测试后再发布

### 4️⃣ 避免循环依赖

⚠️ **禁止**:
- 库中引用特定项目的变量/DB/FB
- 项目 A 的库引用项目 B 的代码
- 创建复杂的跨项目依赖链

✅ **推荐**:
- 库保持纯函数/功能块形式（如当前的实现）
- 通过参数传递外部依赖
- 库之间单向依赖（如果有多个库）

---

## 🧪 验证清单

完成迁移后，请逐项检查：

### 结构验证
- [ ] `0100_项目/01_SharedLibraries/SysLib/` 目录存在且完整
- [ ] `0100_项目/DJ-2026-005_边框缓存机/.plc.json` 配置正确
- [ ] `DJ-2026-005_边框缓存机/OB1/`, `DB1/`, `FB100/`, `Test/` 已迁移
- [ ] 旧的 `DJ-2026-005/` 目录已清理（或标记为已废弃）

### 编译验证
- [ ] LSP 无诊断错误
- [ ] 类型补全正常显示 SysLib 中的 FB/FC（如 FB_TON, FC_DINT_TO_TIME 等）
- [ ] 跳转到定义能正确跳转到 `01_SharedLibraries/SysLib/` 下的文件

### 功能验证
- [ ] 运行 `valve_test.scltest` 所有测试用例通过
- [ ] 新建的 SCL 文件能正常调用 SysLib 函数
- [ ] 编译无错误、无警告

### 隔离性验证（当有第二个项目时）
- [ ] 项目 A 的全局变量不出现在项目 B 的补全列表
- [ ] 项目 A 修改 DB 不影响项目 B
- [ ] 各项目可以定义同名的本地变量（不冲突）

---

## 📚 参考文档

- **Dynamic Siemens Language Support 官方文档**
  - PLC scopes with `.plc.json`
  - Project Libraries (v1) 说明
  - Type lookups isolation 保证
  - libraries paths 相对路径规则

---

## 🎯 预期成果

实施完成后将实现：

| 特性 | 状态 |
|------|------|
| ✅ 项目集中管理 | 所有PLC项目统一在 `0100_项目` 下 |
| ✅ 多项目共用 SysLib | 一个库源，多处引用 |
| ✅ 类型隔离 | 项目间零冲突 |
| ✅ 统一维护 | 修改一处，全局生效 |
| ✅ 版本一致 | 避免副本 divergence |
| ✅ 符合插件规范 | 使用官方推荐的 libraries 机制 |

---

## 📌 执行顺序总结

**立即执行（本次任务）**:
1. ✅ 创建 `0100_项目/01_SharedLibraries/SysLib/` 目录
2. ✅ 迁移 SysLib 内容从 `DJ-2026-005/SysLib/` 到共享位置
3. ✅ 迁移 PLC 源码 (`OB1/`, `DB1/`, `FB100/`, `Test/`) 到 `DJ-2026-005_边框缓存机/`
4. ✅ 在新位置创建并配置 `.plc.json`
5. ✅ 清理旧位置的文件
6. ✅ 验证编译和测试通过

**后续优化（可选）**:
7. 初始化 Git 版本管理
8. 编写 SysLib 使用文档
9. 建立库的更新流程规范
10. 添加第二个项目验证隔离性
