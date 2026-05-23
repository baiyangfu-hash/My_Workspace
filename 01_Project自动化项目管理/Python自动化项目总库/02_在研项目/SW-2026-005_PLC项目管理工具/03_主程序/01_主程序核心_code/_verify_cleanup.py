import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('=== 1. 检查已删模块是否仍可导入 ===')
modules_to_check = [
    ('src.services.hmi_service', 'hmi_service'),
    ('src.services.plc_service', 'plc_service'),
    ('src.services.test_management_service', 'test_management_service'),
    ('src.ui.widgets.hmi_mapper', 'hmi_mapper'),
    ('src.ui.widgets.io_table', 'io_table'),
    ('src.ui.widgets.test_runner_panel', 'test_runner_panel'),
    ('src.ui.widgets.variable_checker', 'variable_checker'),
]
for mod_path, mod_name in modules_to_check:
    try:
        __import__(mod_path)
        print(f'  WARNING {mod_name}: still importable!')
    except (ImportError, ModuleNotFoundError):
        print(f'  OK {mod_name}: deleted successfully')

print()
print('=== 2. Core module import test ===')
core_modules = [
    ('src.core.app', 'Application'),
    ('src.ui.main_window', 'MainWindow'),
    ('src.ui.managers.menu_manager', 'MenuManager'),
    ('src.core.event_bus', 'EventBus'),
    ('src.sync.sync_engine', 'SyncEngine'),
]
for mod_path, cls_name in core_modules:
    try:
        mod = __import__(mod_path, fromlist=[cls_name])
        getattr(mod, cls_name)
        print(f'  OK {mod_path}.{cls_name}')
    except Exception as e:
        print(f'  FAIL {mod_path}.{cls_name}: {e}')

print()
print('=== 3. main_window.py line count ===')
mw_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'ui', 'main_window.py')
with open(mw_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f'  Current: {len(lines)} lines (was 1293)')

print()
print('=== 4. Residual reference scan ===')
import subprocess
result = subprocess.run(
    ['grep', '-rn', 'hmi_service\|plc_service\|test_management_service\|hmi_mapper\|io_table\|test_runner_panel\|variable_checker', 'src/', '--include=*.py'],
    capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
)
if result.stdout.strip():
    print('  Found residual references:')
    for line in result.stdout.strip().split('\n'):
        print(f'    {line}')
else:
    print('  No residual references found - CLEAN!')
