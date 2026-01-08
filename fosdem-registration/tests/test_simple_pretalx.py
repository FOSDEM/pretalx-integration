"""
Simple functional test script that uses pretalx's test infrastructure.
Run with: python -m pretalx test fosdem_registration.tests.test_simple_pretalx
"""
from django.test import TestCase

from fosdem_registration.models import FosdemRegistrationGuardian


class SimpleFosdemRegistrationTest(TestCase):
    """Simple test using Django's TestCase."""

    def test_create_guardian(self):
        """Test creating a guardian model."""
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Test Parent",
            email="parent@example.com",
            contact_number="+32470123456",
        )

        self.assertEqual(guardian.name, "Test Parent")
        self.assertEqual(guardian.email, "parent@example.com")
        self.assertEqual(guardian.contact_number, "+32470123456")
        self.assertTrue(guardian.pk)

    def test_guardian_str(self):
        """Test guardian string representation."""
        guardian = FosdemRegistrationGuardian(
            name="Jane Doe",
            email="jane@example.com",
            contact_number="+1234567890",
        )
        # Should have some string representation
        str_repr = str(guardian)
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)
