import pytest
from scripts.qa.legacy.auto_test_all import AutoTestRunner


def test_runner_all_pass(monkeypatch):
    runner = AutoTestRunner()

    # 提供两个假的测试函数均返回 True
    def ok1():
        return True
    def ok2():
        return True

    runner.start()
    runner.test('t1', ok1)
    runner.test('t2', ok2)
    summary = runner.finish()

    assert summary['total'] == 2
    assert summary['passed'] == 2
    assert summary['failed'] == 0


def test_runner_handles_exception(monkeypatch):
    runner = AutoTestRunner()

    def boom():
        raise RuntimeError('fail')

    runner.start()
    runner.test('t1', boom)
    summary = runner.finish()

    assert summary['total'] == 1
    assert summary['passed'] == 0
    assert summary['failed'] == 1
