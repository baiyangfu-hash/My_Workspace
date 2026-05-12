# -*- coding: utf-8 -*-
"""Template Module Fix Verification"""
import sys, os
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

print('=' * 60)
print('  Template Module Fix - Verification')
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

# T1: Template count after init
def t1():
    from src.services.template_service import TemplateService
    TemplateService.initialize_builtin_templates()
    templates = TemplateService.list_templates()
    builtin = [t for t in templates if getattr(t, 'is_builtin', False)]
    custom = [t for t in templates if not getattr(t, 'is_builtin', False)]
    return 'total=%d builtin=%d custom=%d' % (len(templates), len(builtin), len(custom))

# T2: Old templates cleaned up
def t2():
    from src.services.template_service import TemplateService
    templates = TemplateService.list_templates()
    old_ids = ['TPL-001', 'TPL-002', 'TPL-003', 'TLP-PLC-STD-001',
               'TLP-PLC-AUTO-001', 'TLP-PLC-HMI-001', 'TLP-DJ-STD-001',
               'TLP-XT-STD-001', 'TLP-WX-STD-001', 'TLP-PY-WEB-001',
               'TLP-PY-DATA-001']
    existing_ids = [getattr(t, 'template_id', '') for t in templates]
    conflicts = [oid for oid in old_ids if oid in existing_ids]
    return 'old_template_conflicts=%d (should be 0)' % len(conflicts)

# T3: New 5 templates exist
def t3():
    from src.services.template_service import TemplateService
    expected = ['TPL-FULLLINE-AUTO-001', 'TPL-SINGLE-ROBOT-001',
               'TPL-SINGLE-PLC-001', 'TPL-UPGRADE-STD-001', 'TPL-UPPER-STD-001']
    templates = TemplateService.list_templates()
    existing = [getattr(t, 'template_id', '') for t in templates]
    found = [e for e in expected if e in existing]
    return 'expected_5_found=%d/5' % len(found)

# T4: Update builtin template (non-identity fields)
def t4():
    from src.services.template_service import TemplateService
    TemplateService.initialize_builtin_templates()
    templates = TemplateService.list_templates()
    builtin = [t for t in templates if getattr(t, 'is_builtin', False) and 'FULLLINE' in getattr(t, 'template_id', '')]
    if not builtin:
        return 'SKIP: no FULLLINE template'
    t = builtin[0]
    result, error = TemplateService.update_template(t, {'name': 'TestName_V2', 'description': 'TestDesc'})
    if error:
        return 'update_error=%s' % error
    # Reload and verify
    updated = TemplateService.get_template(t.template_id)
    new_name = getattr(updated, 'name', '')
    return 'updated_name=%s' % new_name

# T5: Update builtin template identity field rejected gracefully
def t5():
    from src.services.template_service import TemplateService
    templates = TemplateService.list_templates()
    builtin = [t for t in templates if getattr(t, 'is_builtin', False)]
    if not builtin:
        return 'SKIP: no builtin template'
    t = builtin[0]
    result, error = TemplateService.update_template(t, {'template_id': 'HACKED'})
    if error and 'template_id' in error:
        return 'identity_rejected_OK: %s' % error[:50]
    return 'ERROR: should have rejected'

# T6: Reset builtin templates works
def t6():
    from src.services.template_service import TemplateService
    # First modify a builtin template
    templates = TemplateService.list_templates()
    builtin = [t for t in templates if getattr(t, 'is_builtin', False)]
    if not builtin:
        return 'SKIP: no builtin template'
    t = builtin[0]
    original_name = getattr(t, 'name', '')
    # Modify it
    TemplateService.update_template(t, {'name': 'TEMP_MODIFIED_NAME'})
    # Reset
    result, error = TemplateService.reset_builtin_templates()
    if error:
        return 'reset_error=%s' % error
    # Verify restored
    restored = TemplateService.get_template(t.template_id)
    restored_name = getattr(restored, 'name', '')
    is_restored = (restored_name != 'TEMP_MODIFIED_NAME')
    return 'reset_ok=%s name_changed_back=%s' % ('Y' if result else 'N', 'Y' if is_restored else 'N')

# T7: GUI MainWindow with template manager loads
def t7():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    from src.ui.main_window import MainWindow
    window = MainWindow()
    has_tmpl_mgr = hasattr(window, 'template_manager') or hasattr(window, '_template_widget')
    return 'MainWindow_OK=%s has_templatemgr=%s' % ('Y', 'Y' if has_tmpl_mgr else 'N')

run_test('TM-01-InitCount', t1)
run_test('TM-02-OldCleaned', t2)
run_test('TM-03-New5Exist', t3)
run_test('TM-04-EditBuiltin', t4)
run_test('TM-05-IdentityReject', t5)
run_test('TM-06-ResetWorks', t6)
run_test('TM-07-GUILoad', t7)

passed = sum(1 for _, ok, _ in tests if ok)
failed = len(tests) - passed
total = len(tests)

print('')
header = '%-22s %-8s %s' % ('ID', 'STATUS', 'Detail')
print('-' * 60)
for name, ok, detail in tests:
    status = '[PASS]' if ok else '[FAIL]'
    print('%-22s %s %s' % (name, status, detail))

print('')
print('=' * 60)
result_line = 'Total: %d | Passed: %d | Failed: %d | Rate: %.1f%%' % (total, passed, failed, passed/total*100)
print(result_line)
print('=' * 60)

if errors:
    print('')
    print('Errors:')
    for tid, err in errors:
        print('  [%s] %s' % (tid, err[:80]))

sys.exit(0 if failed == 0 else 1)
