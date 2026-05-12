# -*- coding: utf-8 -*-
"""SW-2026-004 Regression Test V2"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

print('=' * 60)
print('  SW-2026-004 Regression Test V2')
print('=' * 60)

errors = []
tests = []

def run_test(name, fn):
    try:
        result = fn()
        tests.append((name, True, result))
    except Exception as e:
        errors.append((name, str(e)))
        tests.append((name, False, str(e)))

def t01():
    from src.core.config import Config
    Config.load_config()
    return 'Config OK'

def t02():
    from src.core.version import VERSION
    return f'VERSION={VERSION}'

def t03():
    from src.utils.logger import setup_logger
    setup_logger('rt')
    return 'OK'

def t04():
    from src.core.constants import DEFAULT_TEMPLATES
    tpl_count = len(DEFAULT_TEMPLATES)
    return f'templates={tpl_count}'

def t05():
    from src.models.project import Project
    p = Project(id='t', code='TEST', name='Test', path='/tmp/t')
    return f'{p.code} OK'

def t06():
    from src.models.change import Change, Domain, Nature, Scope
    co = Change(
        change_id='CHG-PLC-2026-001',
        project_id='proj-001',
        title='Test',
        domain=Domain.PLC,
        nature=Nature.OPT,
        scope=Scope.LOCAL
    )
    return f'{co.change_id} OK'

def t07():
    from src.dao.database import Database
    db = Database()
    db.create_tables()
    return 'create_tables OK'

def t08():
    from src.services.project_service import ProjectService
    methods = [x for x in dir(ProjectService) if not x.startswith('_')]
    return f'methods={len(methods)}'

def t09():
    from src.services.library_dependency_service import LibraryDependencyService
    svc = LibraryDependencyService()
    return f'get_deps={hasattr(svc, "get_dependencies")}'

def t10():
    from src.services.change_service import ChangeService
    svc = ChangeService()
    return f'get_chg={hasattr(svc, "get_project_changes")} gen={hasattr(svc, "generate_change_document")}'

def t11():
    from src.services.build_deploy_service import BuildDeployService
    svc = BuildDeployService()
    methods = [x for x in dir(svc) if not x.startswith('_')]
    return f'methods={len(methods)}'

def t12():
    from src.services.check_service import CheckService
    return 'OK'

def t13():
    from src.services.report_service import ReportService
    return 'OK'

def t14():
    from src.core.spec_manager import SpecManager
    SpecManager()
    return 'OK'

def t15():
    from src.services.plugin_market_service import PluginMarketService
    PluginMarketService()
    return 'OK'

def t16():
    from PyQt5.QtWidgets import QApplication, QMainWindow
    return 'PyQt5 OK'

def t17():
    from src.ui.main_window import MainWindow
    return 'MainWindow OK'

def t18():
    from src.ui.widgets.change_manager import ChangeManagerWidget
    return 'ChangeManager OK'

run_test('T01-BasicImport', t01)
run_test('T02-Version', t02)
run_test('T03-Logger', t03)
run_test('T04-Constants', t04)
run_test('T05-ProjectModel', t05)
run_test('T06-ChangeModel', t06)
run_test('T07-Database', t07)
run_test('T08-ProjectSvc', t08)
run_test('T09-DepSvc', t09)
run_test('T10-ChangeSvc', t10)
run_test('T11-BuildSvc', t11)
run_test('T12-CheckSvc', t12)
run_test('T13-ReportSvc', t13)
run_test('T14-SpecMgr', t14)
run_test('T15-PluginSvc', t15)
run_test('T16-PyQt5', t16)
run_test('T17-MainWindow', t17)
run_test('T18-ChangeMgrWidget', t18)

passed = sum(1 for _, ok, _ in tests if ok)
failed = len(tests) - passed
total = len(tests)

print()
header = f"{'ID':<20} {'STATUS':<8} Detail"
print(header)
print('-' * 60)
for name, ok, detail in tests:
    status = '[PASS]' if ok else '[FAIL]'
    print(f'{name:<20} {status:<8} {detail}')

print()
print('=' * 60)
result_line = f'Total: {total} | Passed: {passed} | Failed: {failed} | Rate: {passed/total*100:.1f}%'
print(result_line)
print('=' * 60)

if errors:
    print()
    print('Error Details:')
    for tid, err in errors:
        print(f'  [{tid}] {err}')

sys.exit(0 if failed == 0 else 1)
