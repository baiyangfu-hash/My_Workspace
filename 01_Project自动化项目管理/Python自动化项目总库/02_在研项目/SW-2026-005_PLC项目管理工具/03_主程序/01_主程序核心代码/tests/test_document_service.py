from pathlib import Path

import pytest

from src.core.constants import DocumentType
from src.services.document_service import DocumentService


@pytest.mark.parametrize(
    "doc_type",
    [
        DocumentType.REQ,
        DocumentType.DSN,
        DocumentType.IFC,
        DocumentType.UM,
        DocumentType.CHG,
        DocumentType.ALM,
        DocumentType.VAR,
        DocumentType.IO,
        DocumentType.ARC,
        DocumentType.TEST,
        DocumentType.SUM,
    ],
)
def test_template_contains_basic_header_fields(doc_type):
    content = DocumentService._get_template_content(
        doc_type=doc_type,
        title="标题测试",
        version="V9.9.9",
        author="tester",
    )

    assert content.startswith("# 标题测试")
    assert "版本: V9.9.9" in content
    assert "作者: tester" in content


def test_create_document_uses_template_when_content_is_none(tmp_path: Path):
    project_root = tmp_path / "DemoProject"
    project_root.mkdir(parents=True)

    doc_path, error = DocumentService.create_document(
        project_path=str(project_root),
        doc_type=DocumentType.IFC,
        doc_name="接口文档",
        version="V1.0.0",
        author="tester",
        content=None,
    )

    assert error is None
    assert doc_path is not None
    path = Path(doc_path)
    assert path.exists()
    assert "版本: V1.0.0" in path.read_text(encoding="utf-8")

