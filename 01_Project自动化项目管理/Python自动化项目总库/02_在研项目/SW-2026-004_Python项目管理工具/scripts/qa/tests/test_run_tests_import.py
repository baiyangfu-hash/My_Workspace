import importlib
import scripts.qa.legacy.run_tests as run_tests_mod


def test_run_tests_module_importable():
    # 仅确认模块可安全导入（heavy imports 在 main() 内延迟）
    importlib.reload(run_tests_mod)
    assert hasattr(run_tests_mod, 'main')
