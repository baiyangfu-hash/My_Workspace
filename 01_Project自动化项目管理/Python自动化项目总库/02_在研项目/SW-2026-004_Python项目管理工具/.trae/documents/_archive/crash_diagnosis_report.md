# 插件配置闪退及全系统深度诊断报告

**诊断时间**: 2026-04-11  
**触发操作**: 点击"配置插件"按钮后程序闪退  
**严重程度**: 🔴 致命（导致程序崩溃）

---

## 🚨 闪退根本原因（已确认）

### 问题#CRASH-1: `PluginService.update_plugin()` 参数签名完全不匹配 ⭐⭐⭐⭐⭐

| 项目 | 详情 |
|------|------|
| **文件** | [plugin_manager.py:330-338](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理/Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心代码/src/ui/widgets/plugin_manager.py#L330-L338) |
| **错误类型** | `TypeError: update_plugin() got an unexpected keyword argument 'name'` |
| **原因** | 调用时传了6个关键字参数(name/version/author/description/status/config)，但方法只接受3个位置参数(plugin_id/new_version/new_path) |

#### 错误代码（当前实现 ❌）
```python
# plugin_manager.py:330-338
success, error = PluginService.update_plugin(
    plugin.plugin_id,
    name=new_config["name"],          # ❌ 参数不存在！
    version=new_config["version"],      # ❌ 参数不存在！
    author=new_config["author"],        # ❌ 参数不存在！
    description=new_config["description"],  # ❌ 参数不存在！
    status=new_config["status"],        # ❌ 参数不存在！
    config=new_config["config"]         # ❌ 参数不存在！
)
```

#### 实际方法签名（plugin_service.py:294）
```python
@staticmethod
def update_plugin(plugin_id: str, new_version: str, new_path: str = None) -> tuple[bool, str]:
    """更新插件到新版本"""  # ← 这是用于版本升级的，不是用于编辑属性！
```

#### 可用的正确方法
```python
# 方法1: 使用 DAO 直接更新
PluginDAO.update(plugin_id, {"name": ..., "version": ..., ...})

# 方法2: 使用专门的配置更新方法
PluginService.update_plugin_config(plugin_id, {"key": "value"})
```

#### 修复方案
```python
# 正确的实现方式
from src.dao.plugin_dao import PluginDAO

if dialog.exec_() == QDialog.Accepted:
    try:
        success, error = PluginDAO.update(
            plugin.plugin_id,
            {
                "name": self.cfg_name.text().strip(),
                "version": self.cfg_version.text().strip(),
                "author": self.cfg_author.text().strip(),
                "description": self.cfg_description.toPlainText().strip(),
                "status": self.cfg_status.currentText(),
                "config": self.cfg_params_text.toPlainText().strip()
            }
        )
        if not success:
            QMessageBox.critical(self, "错误", f"保存失败")
            return
        
        self._load_plugins()
        QMessageBox.information(self, "成功", "插件配置已保存")
        
    except Exception as e:
        logger.exception(f"配置插件时发生异常: {e}")
        QMessageBox.critical(self, "错误", f"配置插件时出错:\n{str(e)}")
```

---

## ⚠️ 其他潜在问题点（可能导致其他功能异常）

### 问题#POTENTIAL-2: `_on_settings()` 中 Config 可能未初始化

| 项目 | 详情 |
|------|------|
| **文件** | [main_window.py](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理\Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序核心_code/src/ui/main_window.py) 的 `_on_settings()` 方法 |
| **风险** | 如果 Config._config_dir 未设置，Config.get/set/save 会抛出 RuntimeError |
| **触发条件** | 用户点击菜单"工具→设置"时 |

**防护方案**：
```python
def _on_settings(self):
    try:
        from PyQt5.QtWidgets import QDialog, ...
        
        dialog = QDialog(self)
        # ... 对话框构建代码 ...
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                Config.set("default_project_path", ...)
                Config.set("auto_save", ...)
                Config.set("log_level", ...)
                Config.save()
                QMessageBox.information(self, "成功", "设置已保存")
            except Exception as e:
                logger.warning(f"保存设置失败: {e}")
                QMessageBox.warning(self, "警告", f"部分设置未能保存:\n{str(e)}")
    
    except Exception as e:
        logger.exception(f"打开设置对话框时出错: {e}")
        QMessageBox.critical(self, "错误", f"无法打开设置:\n{str(e)}")
```

### 问题#POTENTIAL-3: `_on_run_check()` 中 CheckService 返回值格式未知

| 项目 | 详情 |
|------|------|
| **文件** | [main_window.py](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理\Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序_core/src/ui/main_window.py) 的 `_on_run_check()` 方法 |
| **风险** | 假设返回 `(result_dict, error)` 格式，但实际可能是其他格式 |
| **触发条件** | 用户点击菜单"工具→规范检查"时 |

**验证步骤**：
1. 先检查 `CheckService.check_project()` 的实际返回值类型
2. 确保 result.get('results') 存在且是列表
3. 每个 result 项必须有 name、passed、message 字段

### 问题#POTENTIAL-4: `_on_generate_report()` 中 ReportService 参数不匹配

| 项目 | 详情 |
|------|------|
| **文件** | [main_window.py](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理\Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序_core/src/ui/main_window.py) 的 `_on_generate_report()` 方法 |
| **风险** | 调用 `ReportService.generate_report(project, type_key, save_path)` 但该方法可能只接受2个参数 |
| **触发条件** | 用户点击菜单"工具→生成报告"时 |

**验证步骤**：
1. 检查 `ReportService.generate_report()` 的实际函数签名
2. 确认参数顺序和类型是否匹配

### 问题#POTENTIAL-5: `_view_plugin_detail()` 中 plugin 属性访问可能为 None

| 项目 | 详情 |
|------|------|
| **文件** | [plugin_manager.py:369](file:///d:/BaiduSyncdisk/My_Workspace/01_Project自动化项目管理\Python自动化项目总库/02_在研项目/SW-2026-004_Python项目管理工具/03_主程序/01_主程序_core/src/ui/widgets/plugin_manager.py#L369) |
| **风险** | `plugin.status.value` 在 status 为 None 时会抛出 AttributeError |
| **触发条件** | 用户点击"查看详情"且插件的 status 字段为空时 |

**防护代码**：
```python
form.addRow("状态:", QLabel(plugin.status.value if plugin.status and hasattr(plugin.status, 'value') else "-"))
```

---

## 🛠️ 完整修复优先级

### 第一批：立即修复（防止闪退）

1. **[HIGH]** 修复 `_config_plugin()` - 改用 `PluginDAO.update()` 替代错误的 `PluginService.update_plugin()` 调用
2. **[HIGH]** 为所有新实现的对话框添加 try-except 异常保护

### 第二批：验证修复（防止其他闪退）

3. **[MEDIUM]** 验证 `_on_settings()` 的 Config 初始化逻辑
4. **[MEDIUM]** 验证 `_on_run_check()` 的 CheckService 返回值格式
5. **[MEDIUM]** 验证 `_on_generate_report()` 的 ReportService 参数

### 第三步：代码质量改进

6. **[LOW]** 移除 `plugin_manager.py:320` 的重复 `import json`
7. **[LOW]** 统一所有对话框的异常处理模式

---

## ✅ 推荐的立即修复代码

请允许我立即修复问题#CRASH-1（插件配置闪退），这是最紧急的问题。
