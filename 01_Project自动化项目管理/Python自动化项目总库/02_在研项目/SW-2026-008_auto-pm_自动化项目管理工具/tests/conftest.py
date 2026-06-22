import json
import random
from pathlib import Path

import pytest

# botocore likes us-east-1
TEST_AWS_REGION = "us-east-1"
TEST_S3_BUCKET = "test-bucket"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Randomise the order of tests to avoid flakiness."""
    random.shuffle(items)


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """创建临时工作空间，含一个模拟 PLC 项目（对齐 LSP-907 标准目录结构）"""
    project_dir = tmp_path / "DJ-2026-TEST_测试项目"
    project_dir.mkdir()
    # .plc.json
    (project_dir / ".plc.json").write_text(
        json.dumps(
            {
                "name": "DJ-2026-TEST",
                "version": "V1.0.0",
                "description": "测试项目",
                "type": "standard",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # LSP-907 标准目录结构（12 个）
    for d in [
        "00_项目管理", "01_需求与设计", "02_PLC程序", "03_HMI设计",
        "04_现场调试", "04_驱动器与设备", "05_测试与验证", "06_文档与交付",
        "07_技术支持", "08_备件管理", "09_项目总结", "10_知识库",
    ]:
        (project_dir / d).mkdir()
    # PM_SESSION
    (project_dir / "PM_SESSION_DJ-2026-TEST.md").write_text(
        "# PM_SESSION\n", encoding="utf-8"
    )
    # PRD 目录
    (project_dir / "PRD").mkdir()
    return tmp_path
