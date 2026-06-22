"""Test auto_pm."""

import auto_pm


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(auto_pm.__name__, str)
