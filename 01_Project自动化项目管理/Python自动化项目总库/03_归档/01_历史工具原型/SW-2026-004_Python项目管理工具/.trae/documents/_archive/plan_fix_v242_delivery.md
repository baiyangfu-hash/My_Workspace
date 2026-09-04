# V2.4.2 交付物修复计划 — exe重编译 + 模板同步

## 一、问题确认

### 用户反馈
用户用 V2.4.2 创建的新项目 `DJ-2026-001`，目录结构仍是**旧模板**（00/07/10/20/30/40/90 跳号），而非新定义的 00~07 连续编号。

### 根因（双重故障）

| # | 错误 | 影响 | 严重程度 |
|---|------|------|:--------:|
| R1 | **exe 未重新编译** | 打包用的是旧 dist/ 产物，内部源码未更新 | 🔴 致命 |
| R2 | **数据库模板未同步** | `initialize_builtin_templates()` 对已存在模板跳过不更新 | 🔴 致命 |

### 数据流分析

```
用户点击"新建项目"
    ↓
project_service.create_project(template_id="TPL-SINGLE-PLC-001")
    ↓
template_dao.get_by_id("TPL-SINGLE-PLC-001")  ← 【读数据库】非读constants.py!
    ↓
返回数据库中的旧模板数据(旧structure: 28条/跳号)
    ↓
按旧structure生成项目目录 → 用户看到旧结构 ❌
```

---

## 二、修复方案

### Phase A: 重新编译 exe（解决 R1）

**步骤**:
1. 确认 PyInstaller 编译环境和 spec 文件位置
2. 执行 `pyinstaller` 重新编译
3. 验证新生成的 `dist/Python项目管理工具.exe` 包含新代码

**验证方法**: 编译后检查 exe 内嵌的 version.py 是否为 V2.4.2

### Phase B: 确保新 exe 启动时同步模板到数据库（解决 R2）

**方案选择**: 修改 `initialize_builtin_templates()` — 对已存在的内置模板也进行更新对比

**具体修改** (`src/services/template_service.py` L21-L50):

```python
@staticmethod
def initialize_builtin_templates():
    """初始化内置模板到数据库"""
    try:
        valid_builtin_ids = {t["id"] for t in DEFAULT_TEMPLATES}

        # 清理无效旧记录
        existing = TemplateDAO.list_all()
        for t in existing:
            if getattr(t, 'is_builtin', False) and getattr(t, 'template_id', '') not in valid_builtin_ids:
                TemplateDAO.force_delete(getattr(t, 'template_id', ''))

        for template_data in DEFAULT_TEMPLATES:
            template_id = template_data["id"]
            existing_tmpl = TemplateDAO.get_by_id(template_id)

            if existing_tmpl is None:
                # 新建（原逻辑不变）
                template = Template(...)
                TemplateDAO.create(template)
            else:
                # 【新增】已存在则更新为最新定义
                existing_tmpl.name = template_data["name"]
                existing_tmpl.version = template_data["version"]
                existing_tmpl.compiler = template_data["compiler"]
                existing_tmpl.scene = template_data["scene"]
                existing_tmpl.description = template_data["description"]
                existing_tmpl.structure = template_data["structure"]
                existing_tmpl.templates = template_data.get("templates", [])
                existing_tmpl.business_lines = template_data.get("business_lines", [])
                TemplateDAO.update(template_id, existing_tmpl.to_dict())
                logger.info(f"内置模板已更新: {template_id}")

        logger.info("所有内置模板初始化完成")
    except Exception as e:
        logger.exception(f"初始化内置模板失败: {e}")
```

### Phase C: 重新打包交付物

使用新编译的 exe 重复之前的两阶段打包流程：
1. 更新 `06_交付物/` （复制新 exe + 新文档）
2. 打包到 `06_交付物打包/` 

### Phase D: 验证

1. 用新 exe 启动工具
2. 重置内置模板（或删除数据库后重启让 initialize 重新加载）
3. 创建新项目 → 验证目录结构为 00~07 连续编号

---

## 三、执行步骤

### Task 1: 修改 template_service.py — 增量更新逻辑
- 文件: `src/services/template_service.py`
- 修改: `initialize_builtin_templates()` 方法
- 增加: 已存在模板的 update 分支

### Task 2: 重新编译 exe
- 定位 PyInstaller spec 文件
- 执行编译命令
- 确认 dist/ 下生成新 exe

### Task 3: 更新 06_交付物 目录
- 复制新编译的 exe（替换旧的）
- 复制 V2.4.2 发布文档

### Task 4: 打包 V2.4.2 zip
- 两阶段打包（同之前流程）

### Task 5: 验证
- zip 完整性检查
- 功能验证（新建项目→检查目录结构）

---

## 四、不做的事项

- ❌ 不修改项目创建逻辑 (`project_service.py`)
- ❌ 不修改数据模型 (Template 表结构)
- ❌ 不影响已有项目（已有项目的目录不会变）
- ❌ 不改变 `reset_builtin_templates()` 的行为

---

## 五、验收标准

- [ ] AC-01: 新编译的 exe 版本显示 V2.4.2
- [ ] AC-02: 启动后数据库中 TPL-SINGLE-PLC-001 的 structure 为 8 条（00~07）
- [ ] AC-03: 新建项目目录结构为 00_项目管理 ~ 07_工具与配置 连续编号
- [ ] AC-04: 打包 zip 包含新 exe 且验证通过
