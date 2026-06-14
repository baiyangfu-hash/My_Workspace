from types import SimpleNamespace
from pathlib import Path
import src.services.check_service as cs


def make_project(path: Path, template_id: str = "T1", code: str = "PRJ-TEST"):
    return SimpleNamespace(path=str(path), template_id=template_id, code=code)


def test_check_directory_structure_no_template(monkeypatch, tmp_path):
    project = make_project(tmp_path)

    # 模拟 TemplateService.get_template 返回 None
    import src.services.template_service as ts
    monkeypatch.setattr(ts.TemplateService, 'get_template', staticmethod(lambda tid: None))

    result = cs.CheckResult()
    cs.CheckService._check_directory_structure(project, result)

    # 应该产生一条 warning 表示未找到模板
    assert any(item['rule'] == '目录结构检查' and item['level'] == 'warning' for item in result.items)


def test_check_directory_structure_required_missing(monkeypatch, tmp_path):
    project = make_project(tmp_path)

    # 创建只有可选目录的现有文件夹
    (tmp_path / "docs").mkdir()

    # 模拟模板，包含一个必需目录和一个可选目录
    template = SimpleNamespace(structure=[
        {"path": "src", "required": True},
        {"path": "docs", "required": False}
    ], templates=[])

    import src.services.template_service as ts
    monkeypatch.setattr(ts.TemplateService, 'get_template', staticmethod(lambda tid: template))

    result = cs.CheckResult()
    cs.CheckService._check_directory_structure(project, result)

    # 必需目录缺失应产生 error
    assert any(item['rule'].startswith('目录结构-必填目录缺失') or item['level'] == 'error' for item in result.items)


def test_check_file_naming_basic(tmp_path):
    project = make_project(tmp_path)

    # 创建若干文件用于命名检查
    (tmp_path / 'README.md').write_text('This is README')
    (tmp_path / 'good_name.py').write_text('print(1)')
    (tmp_path / 'Bad Name.py').write_text('print(2)')
    (tmp_path / '01-文档_PROJ.md').write_text('doc')

    result = cs.CheckResult()
    cs.CheckService._check_file_naming(project, result)

    # 应至少检查到一个非法字符（Bad Name.py）
    assert any(item['rule'] == '文件命名-非法字符' or '非法字符' in item['message'] for item in result.items)
