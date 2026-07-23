# 技能与驾驶舱上下文桥接：改造方案

## 背景

经过审查发现，三个技能（pm-workflow 386行、fullstack-engineer 257行、plc-electrical-engineer 167行）合计约 810 行，其中 ~350 行（43%）是重复的"上下文管理 + 门禁流程"。驾驶舱（auto-pm QML GUI）已经具备这些能力（5 个 Domain Bridge、10 个 Service、约束系统），但技能完全不知道驾驶舱的存在。

**核心问题**：技能和驾驶舱是"两条平行轨道"——它们共享同一个后端（auto-pm CLI/Service），但技能每次都要从零开始做上下文恢复（读 PM_SESSION、跑健康检查、问用户"什么模式"），而驾驶舱早已知道当前项目、当前变更单、当前页面。

**目标**：让驾驶舱在用户点击"AI 辅助"时，将当前上下文写入一个 JSON 文件。技能启动时检查这个文件，如果存在则跳过冗余的上下文恢复步骤，直接进入领域工作。

## 数据流

```
用户在驾驶舱 ChangeCenterView 选中一个变更单
    │
    │ 点击 "AI 辅助" 按钮
    ▼
QML 收集状态:
  - mainWindow.currentProjectId / Name / Stack / Phase
  - mainWindow.currentPage (= "changeCenter")
  - root.selectedChangeNumber / selectedChangeDetail
    │
    │ 调用 aiContextBridge.writeAiContext(...)
    ▼
AiContextBridge (Python, ~50 行):
  - 构建 context dict
  - 写入 <workspace_root>/.auto-pm/ai_context.json
    │
    ▼
用户对 AI 说: "帮我推进这个变更" / "fix this change"
    │
    ▼
技能启动:
  1. 检查 .auto-pm/ai_context.json 是否存在
  2. 若存在 → 读取 JSON → 跳过 Step 0-1 → 直接进入领域工作
  3. 若不存在 → 走原有完整流程（兼容无驾驶舱场景）
```

## 改造清单

### 改造 1（新建）：AiContextBridge

**文件**: `auto_pm/ui/qml/bridges/ai_context_bridge.py`（新建）

**内容**: 一个轻量 QObject，只做一件事——把 QML 传来的上下文写入 JSON 文件。

```python
"""AiContext Bridge - 驾驶舱 → AI 技能上下文桥接

将当前驾驶舱状态（项目、变更单、页面）写入 JSON 文件，
供 AI 技能（pm-workflow/fullstack/plc）快速恢复上下文。
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Slot


class AiContextBridge(QObject):
    """驾驶舱 → AI 技能上下文桥接器"""

    def __init__(self, workspace_root: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._workspace_root = Path(workspace_root)

    @Slot(str, str, str, str, str, str, str, str, str, str, result="QVariant")
    def writeAiContext(
        self,
        project_id: str,
        project_name: str,
        stack: str,
        phase: str,
        change_number: str,
        change_title: str,
        change_domain: str,
        change_nature: str,
        change_status: str,
        current_page: str,
    ) -> dict[str, Any]:
        """写入 AI 上下文文件"""
        context = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "auto-pm cockpit",
            "workspace_root": str(self._workspace_root),
            "active_project": {
                "id": project_id,
                "name": project_name,
                "stack": stack,
                "phase": phase,
            },
            "active_change": {
                "number": change_number,
                "title": change_title,
                "domain": change_domain,
                "nature": change_nature,
                "status": change_status,
            },
            "active_page": current_page,
        }

        try:
            ai_dir = self._workspace_root / ".auto-pm"
            ai_dir.mkdir(parents=True, exist_ok=True)
            ctx_file = ai_dir / "ai_context.json"
            ctx_file.write_text(
                json.dumps(context, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return {
                "success": True,
                "file": str(ctx_file),
                "message": f"上下文已写入 ({len(json.dumps(context))} bytes)",
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    @Slot(result="QVariant")
    def clearAiContext(self) -> dict[str, Any]:
        """清除 AI 上下文文件"""
        ctx_file = self._workspace_root / ".auto-pm" / "ai_context.json"
        try:
            if ctx_file.exists():
                ctx_file.unlink()
                return {"success": True, "message": "上下文已清除"}
            return {"success": True, "message": "上下文文件不存在，无需清除"}
        except Exception as e:
            return {"success": False, "message": str(e)}
```

**设计要点**:
- 不依赖 Facade/Service 体系，只依赖 `workspace_root`（已在 qml_main_window.py 中可用）
- 不需要 PM_SESSION 摘要——技能可以自己读 PM_SESSION（文件读取很快），上下文文件只需告诉技能"去读哪个项目的 PM_SESSION"
- 10 个 Slot 参数覆盖所有必要字段，QML 端直接传值

### 改造 2（修改）：qml_main_window.py 注入桥接

**文件**: `auto_pm/ui/qml_main_window.py`

**改动位置 1**: 在 import 区域（约 line 47 附近，其他 bridge import 之后）添加:
```python
from auto_pm.ui.qml.bridges.ai_context_bridge import AiContextBridge
```

**改动位置 2**: 在 bridge 创建区域（约 line 180，`system_bridge = ...` 之后）添加:
```python
ai_context_bridge = AiContextBridge(workspace_root=workspace_root)
```

**改动位置 3**: 在 context property 注入区域（约 line 150+，`setContextProperty` 调用区域）添加:
```python
engine.rootContext().setContextProperty("aiContextBridge", ai_context_bridge)
```

**改动量**: 3 行新增，0 行修改。

### 改造 3（修改）：ChangeCenterView.qml 添加"AI 辅助"按钮

**文件**: `auto_pm/ui/qml/views/ChangeCenterView.qml`

**改动位置**: 在导航栏按钮区域，line 188（"台账对账"按钮之后、"新建变更"按钮之前）插入:

```qml
PrimaryButton {
    text: "🤖 AI 辅助"
    type: "primary"
    Layout.preferredWidth: 90
    Layout.preferredHeight: 28
    enabled: typeof aiContextBridge !== "undefined"
             && aiContextBridge !== null
             && root.selectedChangeNumber !== ""
    onClicked: {
        var detail = root.selectedChangeDetail || {}
        var result = aiContextBridge.writeAiContext(
            root.selectedProjectId,
            mainWindow.currentProjectName,
            mainWindow.currentProjectStack,
            mainWindow.currentProjectPhase,
            root.selectedChangeNumber,
            detail.title || "",
            detail.domain || "",
            detail.business_nature || detail.nature || "",
            detail.status || "",
            mainWindow.currentPage
        )
        if (result && result.success) {
            console.log("[QML] AI 上下文已写入: " + result.file)
        } else {
            console.warn("[QML] AI 上下文写入失败: "
                + (result ? result.message : "未知错误"))
        }
    }
}
```

**条件**: 仅当用户选中了变更单时按钮才可用（`root.selectedChangeNumber !== ""`），避免空上下文。

**改动量**: ~25 行新增。

### 改造 4（修改）：pm-workflow SKILL.md 添加驾驶舱模式

**文件**: `.trae/skills/pm-workflow/SKILL.md`

**改动位置**: 在 Step 0 之后、Step 1 之前，插入新的 Step 0.5：

```markdown
### Step 0.5：检查 cockpit AI 上下文（若存在则跳过 Step 0-1）

1. 检查 `<工作空间根>/.auto-pm/ai_context.json` 是否存在
2. **若存在**：
   - 读取 JSON，提取 `active_project`、`active_change`、`active_page`
   - 从 `active_project` 获取：项目 ID、名称、技术栈、阶段
   - 从 `active_change` 获取：变更单号、标题、领域、性质、状态
   - **跳过 Step 0**（venv 激活、`project show`、PM_SESSION 读取、健康检查）
   - **跳过 Step 1**（模式选择），模式由 `active_page` 推断：
     - `changeCenter` → 变更/缺陷/发布模式
     - `workspace` → 项目推进模式
     - `specCenter` → 规范模式
   - 在状态摘要中标注"上下文来源: cockpit AI 辅助"
   - 根据 `active_change` 的 `domain` 字段判断目标技能：
     - `PLC` → 后续直接调用 `plc-electrical-engineer`
     - `SCPT` / `PYTHON` → 后续直接调用 `fullstack-engineer`
3. **若不存在**：继续执行原有 Step 0 和 Step 1（不受影响）
```

**改动量**: ~15 行新增。

### 改造 5（修改）：fullstack-engineer SKILL.md 添加驾驶舱模式

**文件**: `.trae/skills/fullstack-engineer/SKILL.md`

**改动位置**: 在"开始前" section 的 item 1（venv 激活）之后，插入 item 1.5：

```markdown
1.5. 检查 `<工作空间根>/.auto-pm/ai_context.json` 是否存在：
   - **若存在**：读取 JSON，提取 `active_project`、`active_change`。
     跳过后续的 PM_SESSION 读取（items 2-3），直接使用 cockpit 上下文。
     从 `active_change` 中获取变更单上下文（编号、标题、领域、状态）。
   - **若不存在**：继续执行 items 2-4（原有流程，不受影响）。
```

**改动量**: ~5 行新增。

### 改造 6（修改）：plc-electrical-engineer SKILL.md 添加驾驶舱模式

**文件**: `.trae/skills/plc-electrical-engineer/SKILL.md`

**改动位置**: 在 Step 0（venv 激活）之后，Step 1（读 PM_SESSION）之前，插入 Step 0.5：

```markdown
### Step 0.5：检查 cockpit AI 上下文（若存在则跳过 Step 1）

1. 检查 `<工作空间根>/.auto-pm/ai_context.json` 是否存在
2. **若存在**：
   - 读取 JSON，提取 `active_project`、`active_change`
   - 从 `active_change` 获取变更单上下文（编号、标题、领域、性质、状态）
   - **跳过 Step 1**（PM_SESSION 读取 + CHG 读取），直接进入 Step 2（任务路由）
   - 在输出中标注"上下文来源: cockpit AI 辅助"
3. **若不存在**：继续执行 Step 1（原有流程，不受影响）

注意：Step 0（venv 激活）**不跳过**，因为 PLC 技能需要 venv 来运行 `auto-pm plc check`。
```

**改动量**: ~10 行新增。

## 实施顺序

| 步骤 | 文件 | 操作 | 改动量 | 依赖 |
|------|------|------|--------|------|
| 1 | `ai_context_bridge.py` | 新建 | ~50 行 | 无 |
| 2 | `qml_main_window.py` | 3 行新增 | ~3 行 | 步骤 1 |
| 3 | `ChangeCenterView.qml` | 插入按钮 | ~25 行 | 步骤 2 |
| 4 | `pm-workflow/SKILL.md` | 插入 Step 0.5 | ~15 行 | 无 |
| 5 | `fullstack-engineer/SKILL.md` | 插入 item 1.5 | ~5 行 | 无 |
| 6 | `plc-electrical-engineer/SKILL.md` | 插入 Step 0.5 | ~10 行 | 无 |

步骤 1-3（驾驶舱侧）和步骤 4-6（技能侧）可以并行实施。

## 上下文 JSON 格式

```json
{
  "generated_at": "2026-07-23T14:30:00+00:00",
  "source": "auto-pm cockpit",
  "workspace_root": "c:/Users/fubai/Desktop/My_Workspace",
  "active_project": {
    "id": "DJ-2026-022",
    "name": "周单机模板",
    "stack": "plc",
    "phase": "developing"
  },
  "active_change": {
    "number": "CHG-SCPT-2026-145",
    "title": "修复阀门控制时序错误",
    "domain": "PLC",
    "nature": "DEF",
    "status": "draft"
  },
  "active_page": "changeCenter"
}
```

## 验证方案

### 驾驶舱侧验证

1. 启动 cockpit: `python -m auto_pm gui -w "c:\Users\fubai\Desktop\My_Workspace"`
2. 导航到变更中心 → 选中一个变更单
3. 点击 "🤖 AI 辅助" 按钮
4. 检查 `c:\Users\fubai\Desktop\My_Workspace\.auto-pm\ai_context.json` 已创建且格式正确

### 技能侧验证

1. 在 cockpit 中点击 "🤖 AI 辅助" 后，触发 pm-workflow 技能
2. 验证：技能跳过 Step 0（不运行 `auto-pm project show`）、跳过 Step 1（不询问模式）
3. 验证：技能直接进入变更模式，使用 `active_change` 的上下文
4. 删除 `ai_context.json`，再次触发技能 → 验证回退到原有完整流程

### 边界情况

- 未选中变更单时点击按钮 → 按钮 disabled，不可点击
- 未选中项目时 → 按钮 disabled（`root.selectedProjectId` 为空）
- `.auto-pm/` 目录不存在 → 自动创建
- 技能侧 JSON 文件不存在 → 回退到原有流程

## 不做什么（明确排除）

- **不包含 PM_SESSION 摘要**：上下文文件只提供项目/变更/页面元数据，不包含 PM_SESSION 内容。技能仍需自己读 PM_SESSION（文件读取很快），但上下文文件告诉它"读哪个项目的 PM_SESSION"。
- **不在其他页面添加按钮**：初期只在 ChangeCenterView 添加，后续可根据需要扩展到 WorkspaceView、SpecCenterView。
- **不修改约束系统**：约束系统（`auto-pm constraint`）保持不变，后续可考虑将门禁检查集成到 cockpit 按钮中。
- **不修改 fullstack/plc 技能的完整结构**：本次只添加上下文文件检查，不重构技能的其他部分。完整瘦身是后续工作。

## 预期收益

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| pm-workflow 上下文恢复步骤 | Step 0 + Step 1（~50 行指令） | 跳过（~15 行 check） |
| 用户交互次数 | 每次需回答"什么模式" | 0（模式由 cockpit 推断） |
| 技能启动 token 消耗 | 386 行全部加载 | 可跳过 ~50 行上下文恢复 |
| 驾驶舱与技能的关系 | 两条平行轨道 | 驾驶舱写入 → 技能读取 |