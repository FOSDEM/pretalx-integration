"""
Very simple test to check if pytest-django is working.
"""

import pytest


def test_simple():
    """Simple test that should always pass."""
    assert 1 + 1 == 2


def test_django_import():
    """Test if we can import Django."""
    import django

    assert django.VERSION is not None
