import sys
from pathlib import Path

# 将项目核心代码目录加入 sys.path，确保可以导入顶层包 `src`
CORE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CORE_DIR))

import pytest

@pytest.fixture(autouse=True)
def isolate_filesystem(tmp_path, monkeypatch):
    """为测试提供独立临时目录作为工作目录。"""
    monkeypatch.chdir(tmp_path)
    yield
