"""UI 统一事件契约"""

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class UiEvent:
    """发往前端的统一事件对象"""
    event_name: str
    level: Literal["info", "warning", "error", "success"]
    source: str
    message: str
    payload: dict[str, Any] | None = None
