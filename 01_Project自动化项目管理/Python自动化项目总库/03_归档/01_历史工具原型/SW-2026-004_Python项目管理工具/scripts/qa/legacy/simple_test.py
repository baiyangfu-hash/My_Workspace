# -*- coding: utf-8 -*-
"""
迁移副本：简单测试脚本（改造为函数以便 pytest 调用）
"""
from pathlib import Path
import sys

def run_simple_tests(project_root: Path = None):
    project_root = project_root or Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    sys.path.insert(0, str(project_root))

    results = {}

    # 项目管理服务
    try:
        from src.services.project_service import ProjectService
        # 调用方法（测试代理环境下应被 monkeypatch）
        projects, total = ProjectService.list_projects(size=10)
        stats = ProjectService.get_statistics()
        results['project_service'] = True
    except Exception as e:
        results['project_service'] = False

    # 统计服务
    try:
        from src.services.statistics_service import StatisticsService
        overview = StatisticsService.get_overview()
        results['statistics_service'] = True
    except Exception:
        results['statistics_service'] = False

    # 总库管理服务
    try:
        from src.services.library_service import LibraryService
        libraries = LibraryService.list_libraries()
        results['library_service'] = True
    except Exception:
        results['library_service'] = False

    return results

if __name__ == '__main__':
    import pprint
    print("Running simple tests (legacy)")
    summary = run_simple_tests()
    pprint.pprint(summary)
