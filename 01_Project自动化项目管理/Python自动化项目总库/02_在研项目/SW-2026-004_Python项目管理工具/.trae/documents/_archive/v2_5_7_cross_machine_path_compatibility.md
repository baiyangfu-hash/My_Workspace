# V2.5.7 计划：跨机器路径兼容性修复（相对路径方案）

> **计划日期**: 2026-04-17
> **触发原因**: 交付物中路径硬编码，换电脑运行可能出问题
> **方案选择**: 相对路径 + 交付物自带 Projects 文件夹（用户确认）

---

## 一、设计理念

### 核心原则：**解压即用，零配置**

```
交付物 ZIP 解压后的目录结构：
Python自动化项目管理系统_V2.5.6_20260417/
├── Python项目管理工具.exe    ← 双击即运行
├── config/
│   └── app_config.json       ← default_project_path = "./Projects"
├── data/
│   └── project_manager.db
├── Projects/                 ← 新建项目默认存放位置（自带空文件夹）
│   ├── DJ-2026-001_测试/     ← 用户创建的项目自动放这里
│   └── ...
└── 02_发布说明/
    └── ...
```

**关键优势**:
- ✅ 不依赖任何盘符（D: / E: / C: 都可以）
- ✅ 不依赖任何绝对路径
- ✅ exe 和项目文件在同一目录树内，整体迁移方便
- ✅ 与现有 `_detect_project_base_path()` 策略2 (`{exe_dir}/projects`) 完全一致

---

## 二、问题分析

### 2.1 需要修改的位置

| # | 文件 | 当前值 | 目标值 | 原因 |
|---|------|--------|--------|------|
| 1 | `config/app_config.json` (源码) | `"D:\\Projects"` | `"./Projects"` | 消除硬编码 |
| 2 | `config/app_config.json` (交付物) | `"D:\\Projects"` | `"./Projects"` | 同步更新 |
| 3 | `src/core/config.py:_get_default_config()` | `Path.home()/Projects` | `"./Projects"` | 默认值与交付物一致 |
| 4 | `data/project_manager.db` (libraries.root_path) | 可能含 D: 盘路径 | 清空或改为相对 | 避免数据库传播硬编码路径 |
| 5 | 交付物目录结构 | 无 Projects 文件夹 | 新增 `Projects/` 空目录 | 预置默认项目存放位置 |

### 2.2 路径解析链验证

现有代码 `_update_default_path()` 的回退链：

```
优先级1: 总库 root_path (DB)
    ↓ 无效时
优先级2: _detect_project_base_path()
    ├─ 策略1: 向上搜索工作区结构 (01_Project.../0100_项目)
    ├─ 策略2: {exe所在目录}/projects     ← 我们的方案命中这里!
    └─ 策略3: 临时目录
    ↓ 都失败时
优先级3: os.getcwd()
```

**结论**: 将 `default_project_path` 设为 `./Projects` 后，新建项目时：
- 如果总库 root_path 为空 → 进入策略2 → `{exe_dir}/projects` → 即我们自带的 `Projects/` 文件夹 ✅
- 整个链路天然兼容，无需大改

---

## 三、执行步骤

### Task 1: 修改 app_config.json 为相对路径 (P0)

**文件 A** — `03_主程序/01_主程序核心代码/config/app_config.json`:

```diff
- "default_project_path": "D:\\Projects",
+ "default_project_path": "./Projects",
```

**文件 B** — `06_交付物/01_可执行文件/config/app_config.json`:

```diff
- "default_project_path": "2.5.6",
+ "default_project_path": "./Projects",
```

### Task 2: 修改 config.py 默认值 + 相对路径解析 (P0)

**文件**: `src/core/config.py`

**变更 A** — `_get_default_config()` 默认值：

```diff
- "default_project_path": str(Path.home() / "Projects"),
+ "default_project_path": "./Projects",
```

**变更 B** — 新增相对路径解析方法：

```python
@classmethod
def get_resolved_project_path(cls) -> str:
    """
    获取解析后的项目基础路径（处理相对路径）
    
    规则:
    - 相对路径 (以 ./ 或 ../ 开头，或不含盘符) → 基于 exe 所在目录解析
    - 绝对路径 → 直接使用（验证可写性）
    - 空值 → 回退到 ./Projects
    """
    raw = cls.get("default_project_path", "./Projects")
    if not raw:
        raw = "./Projects"
    
    p = Path(raw)
    
    if p.is_absolute():
        if p.exists() and p.is_dir():
            try:
                (p / ".write_test").touch().unlink()
                return str(p)
            except Exception:
                pass
        # 绝对路径无效，回退到相对路径
        p = Path("./Projects")
    
    # 相对路径：基于 exe 所在目录（冻结环境）或 cwd（开发环境）
    import sys
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path.cwd()
    
    resolved = (base / p).resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return str(resolved)
```

### Task 3: 在交付物中预置 Projects 文件夹 (P0)

**操作**:

```
06_交付物/
├── 01_可执行文件/
│   ├── Python项目管理工具.exe
│   ├── config/
│   └── data/
├── Projects/                    ← 新建此空目录（带 .gitkeep 占位）
│   └── .gitkeep
└── 02_发布说明/
```

同时在源码的打包目录也预置：

```
03_主程序/01_主程序核心代码/
├── dist/
├── config/
├── data/
├── Projects/                   ← 新建
│   └── .gitkeep
└── src/
```

### Task 4: 数据库 root_path 清理 (P1)

**诊断脚本**: 查询 `libraries` 表中的 `root_path` 字段

**清理策略**:
- 若 `root_path` 包含绝对路径（如 `D:\BaiduSyncdisk\...`）→ **清空为空字符串**
- 清空后，运行时会触发 `_detect_project_base_path()` 自动重新检测
- 检测结果将指向 `{exe_dir}/.../0100_项目` 或 `{exe_dir}/Projects`

**注意**: 不删除总库记录本身，只清理其 `root_path` 字段。

### Task 5: 重新打包 V2.5.7 (P1)

基于以上全部修改重新执行 PyInstaller 打包：

1. 版本号: `version.py` → `2.5.7`
2. `app_config.json` → `./Projects`
3. 交付物包含 `Projects/` 文件夹
4. 输出: `Python自动化项目管理系统_V2.5.7_20260417.zip`

### Task 6: 文档更新 (P2)

- `07_技术知识库/08_常见问题/常见问题.md`: 新增"跨机器使用/路径问题"FAQ
- `07_技术知识库/10_版本迭代历史.md`: 补充 V2.5.7 记录
- 更新 `06_交付物/02_发布说明/` 下的文档

---

## 四、不修改的部分

以下代码已具备良好的兼容性，无需改动：

| 模块 | 现有机制 |
|------|----------|
| `main.py:get_base_path()` | `sys.executable.parent` 冻结环境兼容 |
| `new_project_dialog.py:_update_default_path()` | 多级回退链，最终兜底到 cwd |
| `library_service.py:_detect_project_base_path()` | 策略2 已使用 `{base_search}/projects` |
| 数据库文件路径 | `data/project_manager.db` 相对路径 |

---

## 五、验收场景

### 场景 A：标准使用（推荐）

```
1. 用户收到 Python自动化项目管理系统_V2.5.7.zip
2. 解压到任意位置（如 E:\工具\）
3. 目录结构:
   E:\工具\Python项目管理工具\
   ├── Python项目管理工具.exe
   ├── config\app_config.json   ← default_project_path = "./Projects"
   ├── Projects\                ← 预置空目录
   └── data\project_manager.db
4. 双击 exe 运行
5. 新建项目 → 项目自动保存到 E:\工具\Python项目管理工具\Projects\DJ-xxx_xxx\
```

### 场景 B：无 D 盘机器

```
1. 电脑只有 C: 盘
2. 解压到 C:\Users\xxx\Tools\
3. 运行 exe → 新建项目 → C:\Users\xxx\Tools\Projects\DJ-xxx_xxx\
4. ✅ 正常工作，无任何报错
```

### 场景 C：测试文件夹验证

```
1. 解压到 D:\管理工具测试\Python自动化项目管理系统_V2.5.7_20260417\
2. 运行 exe
3. 新建项目 → D:\管理工具测试\...\Projects\DJ-2026-001_测试\
4. ✅ 与当前实际使用一致
```

---

## 六、执行顺序

```
Task 1 (app_config.json → ./Projects)
   ↓
Task 2 (config.py 默认值 + get_resolved_project_path)
   ↓
Task 3 (预置 Projects/ 文件夹 + .gitkeep)
   ↓
Task 4 (DB root_path 诊断与清理)
   ↓
Task 5 (PyInstaller 重新打包 V2.5.7)
   ↓
Task 6 (文档更新)
```

## 七、验收清单

- [ ] `app_config.json` 中 `default_project_path` = `"./Projects"` （无盘符）
- [ ] 交付物目录包含空的 `Projects/.gitkeep` 文件夹
- [ ] 数据库 `libraries.root_path` 不含硬编码绝对路径
- [ ] 在 `管理工具测试` 文件夹解压后运行正常
- [ ] 新建项目默认保存到 `{exe所在目录}/Projects/` 下
