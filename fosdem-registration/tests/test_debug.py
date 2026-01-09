"""
Very simple model test to debug the database creation issue.
"""

import pytest
from django.test import TestCase, TransactionTestCase

from fosdem_registration.models import FosdemRegistrationGuardian


class TestDatabaseSetup(TransactionTestCase):
    """Simple test to check if database setup works - using TransactionTestCase for migrations."""

    def test_guardian_creation(self):
        """Test creating a guardian - simplest possible test."""
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Test Parent",
            email="test@example.com",
            contact_number="+1234567890",
        )
        self.assertEqual(guardian.name, "Test Parent")
        self.assertTrue(guardian.pk)


@pytest.mark.django_db(transaction=True)
class TestDatabaseSetupPytest:
    """Pytest version to test database setup."""

    def test_guardian_creation_pytest(self):
        """Test creating a guardian with pytest."""
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Test Parent Pytest",
            email="pytest@example.com",
            contact_number="+9876543210",
        )
        assert guardian.name == "Test Parent Pytest"
        assert guardian.pk is not None
