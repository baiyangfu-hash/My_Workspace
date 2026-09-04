# V2.5.9 补丁: 总库分类项目数显示为 0 问题修复

## Why

用户测试 V2.5.9 交付物后发现「总库管理 → 分类管理」tab 中所有分类的**项目数均显示为 0**，但左侧总库列表显示有 1 个项目。用户反馈："这个问题不是解决了么？怎么还有"

## 根因分析

### 数据库状态对比

| 表名 | 源码DB (开发环境) | 交付物DB (06_交付物/data/) | 截图实际运行 |
|------|------------------|---------------------------|-------------|
| libraries | 1 | 1 | 1 (正常) |
| **library_projects** | **3** ✅ | **0** ❌ | 有数据(新建项目自动加入) |
| **categories** | **5** ✅ | **0** ❌ | **5** (启动时重建) |
| projects | 3 | 11 | N/A |

### 根因链路

```
打包流程:
  源码 data/project_manager.db (有3条library_projects + 5个categories)
    ↓ 复制到(?)
  06_交付物/data/project_manager.db (library_projects=0, categories=0)
    ↓ 打包进 ZIP
  用户解压运行 EXE
    ↓ initialize_default_library()
  检测到 libraries 表有默认总库 → 跳过初始化 → 不重建分类 ❌
    ↓ 但实际上 categories=0, library_projects=0
  用户看到:
    - 左侧: 总库有1个项目 (可能是运行后新建的)
    - 分类管理: 5个分类每个项目数=0 (因为 library_projects 无匹配记录)
```

### 关键代码路径

**UI 层** ([library_manager.py:314-360](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/ui/widgets/library_manager.py#L314-L360)):
```python
def _load_library_categories(self, library_id):
    categories = LibraryService.list_categories(library_id)
    for category in categories:
        # 按 category_id 过滤查询 library_projects 表
        projects, _ = LibraryService.list_library_projects(
            library_id=library_id,
            category_id=category.category_id  # ← 关联查询
        )
        category_project_counts[category.category_id] = len(projects)
```

**DAO 层** ([library_dao.py:192-227](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/dao/library_dao.py#L192-L227)):
```python
def list_projects(library_id, category_id=None, ...):
    query = session.query(Project).join(
        LibraryProject, Project.project_id == LibraryProject.project_id
    ).filter(LibraryProject.library_id == library_id)
    if category_id:
        query = query.filter(LibraryProject.category_id == category_id)  # ← 匹配 category_id
```

**结论**: 项目数统计依赖 `library_projects.category_id` 字段。如果该表为空或 category_id 为 NULL，所有分类的项目数都为 0。

## What Changes

### Fix 1: 同步正确的数据库到交付物（数据层）

将源码 DB 中的正确数据（library_projects + categories）复制到交付物 DB：

**操作**: 用源码 `data/project_manager.db` 覆盖 `06_交付物/data/project_manager.db` 中的关键表数据

**涉及数据**:
- `library_projects`: 3 条记录（3个项目关联到"单机设备项目"分类）
- `categories`: 5 条预置分类（软件开发/单机设备/自动化整线/系统升级/维保）
- `libraries`: 1 条（确保 root_path 为空）

### Fix 2: 增强 initialize_default_library() 的分类补全逻辑（代码层）

当前逻辑：检测到默认总库存在就跳过，不补全缺失的分类。

**修改**: 即使默认总库已存在，也检查并补全缺失的预置分类（幂等操作）。

```python
# 当前: 总库存在 → 直接返回
# 修改后: 总库存在 → 检查分类是否完整 → 缺失则补全
```

**修改位置**: [library_service.py:535-559](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/services/library_service.py#L535-L559)

### Fix 3: 重新打包 V2.5.9（产出层）

基于以上修改重新执行 PyInstaller 打包。

## Impact

- Affected code: `library_service.py` (initialize_default_library 方法增强)
- Affected data: `06_交付物/data/project_manager.db` (library_projects + categories 表)
- Affected packaging: 需要重新执行 PyInstaller

## Tasks

- [ ] Task 1: 将源码 DB 的 library_projects 和 categories 数据同步到交付物 DB
- [ ] Task 2: 增强 initialize_default_library() 的分类补全逻辑
- [ ] Task 3: 重新 PyInstaller 打包 V2.5.9 并更新 ZIP
- [ ] Task 4: 更新文档（打包版本记录 + 发布说明补充）
