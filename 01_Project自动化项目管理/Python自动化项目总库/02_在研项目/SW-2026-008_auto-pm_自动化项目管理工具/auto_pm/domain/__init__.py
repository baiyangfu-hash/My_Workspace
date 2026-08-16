"""auto_pm.domain - 核心业务领域层统一命名空间"""

from __future__ import annotations

from . import plc
from . import change
from . import spec
from . import vartable
from . import modbus

__all__ = [
    "plc",
    "change",
    "spec",
    "vartable",
    "modbus",
]
