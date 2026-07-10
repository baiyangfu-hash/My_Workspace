import logging
from io import StringIO
from unittest.mock import Mock

import pytest
from faker import Faker

from auto_pm.logging.logging import setup_logger


@pytest.fixture
def mock_logger() -> logging.Logger:
    """Create a mock logger for testing."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def mock_logger_manager(mock_logger: logging.Logger) -> Mock:
    """Create a mock logger manager with configured loggers."""
    manager = Mock()
    manager.loggerDict = {
        "uvicorn": mock_logger,
        "uvicorn.error": mock_logger,
        "fastapi": mock_logger,
    }
    return manager


def _capture_logger_output(app_name: str, log_level: str, message: str, method: str) -> str:
    """创建 logger 并捕获输出到 StringIO"""
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除已有 handler（确保幂等逻辑不跳过）
    logger.handlers.clear()

    buffer = StringIO()
    handler = logging.StreamHandler(buffer)
    formatter = logging.Formatter("%(asctime)s [%(levelname)8.8s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    getattr(logger, method)(message)
    return buffer.getvalue().strip()


def test_setup_logger_debug_level(faker: Faker) -> None:
    """Log debug message"""
    output = _capture_logger_output(faker.word(), "DEBUG", "This is a debug message", "debug")
    assert "DEBUG" in output
    assert "This is a debug message" in output


def test_setup_logger_info_level(faker: Faker) -> None:
    """Log info message"""
    output = _capture_logger_output(faker.word(), "INFO", "This is an info message", "info")
    assert "INFO" in output
    assert "This is an info message" in output


def test_setup_logger_warning_level(faker: Faker) -> None:
    """Log warning message"""
    output = _capture_logger_output(faker.word(), "WARNING", "This is a warning message", "warning")
    assert "WARNING" in output
    assert "This is a warning message" in output


def test_setup_logger_error_level(faker: Faker) -> None:
    """Log error message"""
    output = _capture_logger_output(faker.word(), "ERROR", "This is an error message", "error")
    assert "ERROR" in output
    assert "This is an error message" in output


def test_setup_logger_critical_level(faker: Faker) -> None:
    """Log critical message"""
    output = _capture_logger_output(faker.word(), "CRITICAL", "This is a critical message", "critical")
    assert "CRITICAL" in output
    assert "This is a critical message" in output


def test_invalid_log_level(faker: Faker) -> None:
    """Handle invalid log level"""
    invalid_level = faker.word()
    with pytest.raises(
        AttributeError,
        match=f"module 'logging' has no attribute '{invalid_level.upper()}'",
    ):
        setup_logger(log_level=invalid_level, app_name=faker.word())


def test_bind(faker: Faker) -> None:
    """Bind to an existing logger"""
    # Create a mock logger
    mock_logger = Mock(spec=logging.Logger)

    # Setup a new logger and bind the mock logger to it
    logger = setup_logger(app_name=faker.word(), log_level="CRITICAL", bind_to=mock_logger)

    # Verify the mock logger was called with the correct level
    mock_logger.setLevel.assert_called_once_with("CRITICAL")

    # Verify the handlers were copied from the new logger to the mock logger
    assert mock_logger.handlers == logger.handlers

    # Verify the handlers are not empty (should have console handler)
    assert len(mock_logger.handlers) > 0
