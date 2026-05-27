# V2.5.8 计划：修复 V2.5.7 交付物两个遗留 Bug

> **计划日期**: 2026-04-17
> **触发原因**: 用户解压 V2.5.7 交付物后测试发现两个问题

---

## 一、Bug 现象

### Bug 1: 新建项目路径未改变（严重）

**用户截图证据**:
- 新建项目对话框中「项目路径」显示: `D:\BaiduSyncdisk\My_Workspace\01_Project自动化项目管理\Python自动化项目总库\0100_项目`
- **预期**: 应该基于 `{exe所在目录}\Projects\` 或相对路径解析后的位置

**根因分析**:

`new_project_dialog.py:_update_default_path()` 方法的**完整路径决策链**:

```
_update_default_path() 执行流程:
  1. lib_id = self.lib_combo.currentData()
  2. if lib_id:
       → LibraryService.get_library(lib_id)
       → if lib.root_path 存在且有效 → 直接使用 ❌ 这里是问题根源!
  3. if not base_path:
       → _detect_project_base_path() → 向上搜索工作区结构
       → 找到 01_Project.../0100_项目 → 返回绝对路径 ❌
  4. if not base_path:
       → os.getcwd() 兜底
```

**关键发现**: 整个方法**完全没有读取** `config.get("default_project_path")`！

虽然我们在 `app_config.json` 中设置了 `"default_project_path": "./Projects"`，也在 `config.py` 中新增了 `get_resolved_project_path()` 方法，但 **UI 层从未调用它**。

### Bug 2: 版本号仍显示 V2.5.6（中等）

**用户截图证据**:
- 标题栏显示: `Python项目管理工具 v2.5.6`
- 文件夹名: `Python自动化项目管理系统_V2.5.7_20260417`

**根因分析**:

| 文件 | version 值 | 状态 |
|------|-----------|------|
| `src/core/version.py` | **2.5.7** ✅ | 已正确更新 |
| `config/app_config.json` (源码) | **2.5.6** ❌ | 漏改! |
| `06_交付物/.../app_config.json` | **2.5.6** ❌ | 漏改! |

标题栏大概率从 `app_config.json` 的 `version` 字段读取（而非 `version.py`），导致显示 2.5.6。

---

## 二、修复方案

### Fix 1: new_project_dialog.py — 使用 default_project_path 配置

**文件**: `src/ui/dialogs/new_project_dialog.py`

**修改位置**: `_update_default_path()` 方法，在现有逻辑之前插入配置读取优先级

**变更内容**:

```python
def _update_default_path(self):
    """根据配置、总库、自动检测生成项目路径"""
    try:
        lib_id = self.lib_combo.currentData()
        code = self.code_input.text().strip()
        name = self.name_input.text().strip() or "未命名项目"

        if not code:
            return

        base_path = ""
        path_source = ""

        # === 新增: 优先读取配置文件中的 default_project_path ===
        try:
            from src.core.config import Config
            configured_path = Config.get_resolved_project_path()
            if configured_path:
                base_path = configured_path
                path_source = "配置文件(default_project_path)"
                logger.info(f"使用配置文件的项目基础路径: {configured_path}")
        except Exception as config_err:
            logger.debug(f"读取配置路径失败，回退到原有逻辑: {config_err}")

        # === 原有逻辑: 总库 root_path (作为回退) ===
        if not base_path and lib_id:
            try:
                lib = LibraryService.get_library(lib_id)
                if lib and lib.root_path:
                    from pathlib import Path
                    lib_path = Path(lib.root_path)
                    if lib_path.exists() and lib_path.is_dir():
                        try:
                            test_file = lib_path / ".write_test_tmp"
                            test_file.touch()
                            test_file.unlink()
                            base_path = lib.root_path
                            path_source = "总库root_path(回退)"
                        except Exception as write_err:
                            logger.warning(f"总库root_path不可写: {write_err}")
                    else:
                        path_source = "总库root_path(无效)"
            except Exception as e:
                logger.exception(f"获取总库路径失败: {e}")

        # === 原有逻辑: 自动检测 (二次回退) ===
        if not base_path:
            try:
                detected = LibraryService._detect_project_base_path()
                if detected:
                    base_path = detected
                    path_source = "自动检测路径(回退)"
            except Exception as detect_err:
                logger.exception(f"自动检测路径失败: {detect_err}")

        # === 原有逻辑: cwd (最终兜底) ===
        if not base_path:
            base_path = os.getcwd()
            path_source = "当前工作目录(兜底)"

        if base_path:
            project_dir = f"{code}_{name}"
            full_path = os.path.join(base_path, project_dir)
            self.path_input.setText(full_path)

    except Exception as e:
        logger.exception(f"更新默认路径失败: {e}")
```

**核心变化**: 将 `Config.get_resolved_project_path()` 作为**最高优先级**，原有的总库/自动检测/cwd 全部降为回退选项。

### Fix 2: app_config.json — version 同步到 2.5.7

**文件 A**: `03_主程序/01_主程序核心代码/config/app_config.json`

```diff
- "version": "2.5.6",
+ "version": "2.5.7",
```

**文件 B**: `06_交付物/01_可执行文件/config/app_config.json`

```diff
- "version": "2.5.6",
+ "version": "2.5.7",
```

### Fix 3: 重新打包 V2.5.8 (含上述两修复)

基于 Fix 1 + Fix 2 重新执行 PyInstaller 打包：
- 版本号: `version.py` → **2.5.8**
- `app_config.json` version → **2.5.7** (与代码一致)
- 输出: `Python自动化项目管理系统_V2.5.8_20260417.zip`

---

## 三、执行步骤

| Step | 操作 | 内容 |
|------|------|------|
| 1 | 修改 `new_project_dialog.py` | `_update_default_path()` 增加 `Config.get_resolved_project_path()` 优先级 |
| 2 | 修正源码 `app_config.json` | version 2.5.6 → 2.5.7 |
| 3 | 修正交付物 `app_config.json` | version 2.5.6 → 2.5.7 |
| 4 | 更新 `version.py` | 2.5.7 → 2.5.8 |
| 5 | PyInstaller 重新打包 | 生成新 EXE |
| 6 | 复制 EXE + 创建 ZIP | V2.5.8 归档 |
| 7 | 更新打包记录 + 发布说明 | 文档更新 |

## 四、验收标准

- [ ] 解压 V2.5.8 后运行，标题栏显示 **v2.5.7**（或 v2.5.8）
- [ ] 新建项目对话框的「项目路径」默认指向 `{解压目录}\Projects\DJ-xxx_xxx\`
- [ ] 在无 D 盘机器上解压后，路径自动适配为 `{C盘路径}\Projects\...`
- [ ] 总库 root_path 为空时正确回退到配置路径

## 五、防止回归

本次修复揭示了一个架构问题：**`default_project_path` 配置项定义了但从未被 UI 消费**。今后新增配置项时应同步检查所有消费方。
