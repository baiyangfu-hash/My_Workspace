# ruff: noqa: N802
"""AiContext Bridge - 驾驶舱 ↔ AI 技能上下文桥接（双向）

将当前驾驶舱状态（项目、变更单、页面）写入 JSON 文件，
供 AI 技能（pm-workflow）快速恢复上下文；
同时读取 AI 技能执行结果（门禁/测试/LSP）反馈给驾驶舱展示。

设计原则：
- 轻量 QObject，不依赖 Facade/Service 体系
- 只依赖 workspace_root（已在 qml_main_window.py 中可用）
- 写入 .auto-pm/ai_context.json，技能侧检查此文件决定是否跳过上下文恢复
- 读取 .auto-pm/ai_feedback.json，pm-workflow 统一收集子技能结果后写入
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Slot


class AiContextBridge(QObject):
    """驾驶舱 → AI 技能上下文桥接器

    将 cockpit 当前状态（项目、变更单、页面）写入 JSON 文件。
    AI 技能启动时检查此文件，若存在则跳过冗余的上下文恢复步骤。
    """

    def __init__(self, workspace_root: str, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._workspace_root = Path(workspace_root)

    def _fallback_feedback(self, status: str, summary: str) -> dict[str, Any]:
        return {
            "generated_at": "",
            "status": status,
            "skill": "",
            "change_number": "",
            "changed_files": [],
            "lint_result": {"violations": 0, "errors": 0},
            "test_result": {"passed": 0, "failed": 0, "skipped": 0},
            "plc_check_result": {"violations_count": 0},
            "risks": [],
            "verification": "[待反馈]",
            "summary": summary,
        }

    @Slot(str, result="QVariant")
    def setWorkspaceRoot(self, workspace_root: str) -> dict[str, Any]:
        """更新运行态工作空间根目录。"""
        self._workspace_root = Path(workspace_root)
        return {
            "success": True,
            "workspace_root": str(self._workspace_root),
            "message": f"AiContextBridge 已切换到: {self._workspace_root}",
        }

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
        """写入 AI 上下文文件

        QML 端点击"AI 辅助"按钮时调用，将 cockpit 当前状态序列化到
        <workspace_root>/.auto-pm/ai_context.json。

        Args:
            project_id: 当前选中项目 ID（如 "DJ-2026-022"）
            project_name: 项目名称
            stack: 技术栈（"plc" / "python"）
            phase: 项目阶段（"developing" / "delivering" 等）
            change_number: 当前选中变更单号（如 "CHG-SCPT-2026-145"）
            change_title: 变更单标题
            change_domain: 变更域（"PLC" / "SCPT" / "DOCU" 等）
            change_nature: 变更性质（"DEF" / "OPT" / "FEAT" 等）
            change_status: 变更状态（"draft" / "implementing" 等）
            current_page: 当前 cockpit 页面（"changeCenter" / "workspace" 等）

        Returns:
            {"success": True/False, "file": str, "message": str}
        """
        context = {
            "generated_at": datetime.now(UTC).isoformat(),
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
        """清除 AI 上下文文件

        Returns:
            {"success": True/False, "message": str}
        """
        ctx_file = self._workspace_root / ".auto-pm" / "ai_context.json"
        try:
            if ctx_file.exists():
                ctx_file.unlink()
                return {"success": True, "message": "上下文已清除"}
            return {"success": True, "message": "上下文文件不存在，无需清除"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @Slot(result="QVariant")
    def readAiFeedback(self) -> dict[str, Any]:
        """读取 AI 技能执行结果反馈

        pm-workflow 在子技能执行完毕后，将结果写入
        .auto-pm/ai_feedback.json。驾驶舱读取此文件展示 AI 工作状态。

        Returns:
            {"success": True/False, "feedback": {...} 或 "message": str}
            反馈结构:
            {
                "generated_at": "ISO时间戳",
                "status": "completed" | "failed" | "running",
                "skill": "plc-electrical-engineer" | "fullstack-engineer",
                "change_number": "CHG-PLC-2026-001",
                "changed_files": ["文件路径列表"],
                "lint_result": {"violations": 0, "errors": 0},
                "test_result": {"passed": 0, "failed": 0, "skipped": 0},
                "plc_check_result": {"violations_count": 0},
                "risks": ["风险列表"],
                "verification": "[已验证] 或 [待验证]",
                "summary": "一句话摘要"
            }
        """
        fb_file = self._workspace_root / ".auto-pm" / "ai_feedback.json"
        try:
            if not fb_file.exists():
                return {
                    "success": False,
                    "message": "暂无 AI 反馈，将按空反馈状态渲染",
                    "feedback": self._fallback_feedback("missing", "暂无 AI 反馈"),
                    "feedback_state": "missing",
                }
            content = fb_file.read_text(encoding="utf-8")
            feedback = json.loads(content)
            return {
                "success": True,
                "feedback": feedback,
                "feedback_state": "available",
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "message": f"反馈文件格式错误，将按异常反馈状态渲染: {e}",
                "feedback": self._fallback_feedback("invalid", "AI 反馈文件格式错误"),
                "feedback_state": "invalid",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"读取 AI 反馈失败，将按异常反馈状态渲染: {e}",
                "feedback": self._fallback_feedback("error", "AI 反馈读取失败"),
                "feedback_state": "error",
            }
