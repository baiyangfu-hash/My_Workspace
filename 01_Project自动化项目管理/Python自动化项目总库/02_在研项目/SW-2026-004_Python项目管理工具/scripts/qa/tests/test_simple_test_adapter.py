import sys
from types import SimpleNamespace
from pathlib import Path

import scripts.qa.legacy.simple_test as simple_test


def test_simple_test_monkeypatched(monkeypatch, tmp_path):
    # 插入虚假模块到 sys.modules，替代 heavy services
    fake_project_service = SimpleNamespace()
    fake_project_service.list_projects = staticmethod(lambda size=10: ([], 0))
    fake_project_service.get_statistics = staticmethod(lambda: {})

    fake_stats_service = SimpleNamespace()
    fake_stats_service.get_overview = staticmethod(lambda: {})

    fake_library_service = SimpleNamespace()
    fake_library_service.list_libraries = staticmethod(lambda: [])

    # 注入假模块对象，提供 ProjectService / StatisticsService / LibraryService 属性
    sys.modules['src.services.project_service'] = SimpleNamespace(ProjectService=fake_project_service)
    sys.modules['src.services.statistics_service'] = SimpleNamespace(StatisticsService=fake_stats_service)
    sys.modules['src.services.library_service'] = SimpleNamespace(LibraryService=fake_library_service)

    summary = simple_test.run_simple_tests(project_root=Path(simple_test.__file__).parent)

    assert summary['project_service'] is True
    assert summary['statistics_service'] is True
    assert summary['library_service'] is True
