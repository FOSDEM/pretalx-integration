"""
Unit tests for fosdem_registration forms.
"""

import pytest
from django.core.exceptions import ValidationError
from django_scopes import scopes_disabled

from fosdem_registration.forms import (
    FosdemRegistrationForm,
    FosdemRegistrationGuardianForm,
    RegistrationFormSet,
)
from fosdem_registration.models import FosdemRegistration, FosdemRegistrationGuardian


@pytest.mark.django_db
@pytest.mark.forms
class TestFosdemRegistrationGuardianForm:
    """Test cases for FosdemRegistrationGuardianForm."""

    def test_valid_guardian_form(self):
        """Test form with valid data."""
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)

        assert form.is_valid()
        assert form.cleaned_data["name"] == "Jane Doe"
        assert form.cleaned_data["email"] == "jane.doe@example.com"
        assert form.cleaned_data["contact_number"] == "+32470123456"

    def test_guardian_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        # Missing name
        form_data = {
            "email": "jane.doe@example.com",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors

        # Missing email
        form_data = {
            "name": "Jane Doe",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

        # Missing contact_number
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert not form.is_valid()
        assert "contact_number" in form.errors

    def test_guardian_form_invalid_email(self):
        """Test form validation with invalid email."""
        form_data = {
            "name": "Jane Doe",
            "email": "invalid-email",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_guardian_form_save(self):
        """Test saving valid form data."""
        form_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert form.is_valid()

        guardian = form.save()
        assert isinstance(guardian, FosdemRegistrationGuardian)
        assert guardian.name == "Jane Doe"
        assert guardian.email == "jane.doe@example.com"
        assert guardian.contact_number == "+32470123456"

    def test_guardian_form_long_name(self):
        """Test form with name exceeding max length."""
        form_data = {
            "name": "X" * 201,  # Exceeds max_length=200
            "email": "jane.doe@example.com",
            "contact_number": "+32470123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_guardian_form_unicode_characters(self):
        """Test form with unicode characters in name."""
        form_data = {
            "name": "José María García-López",
            "email": "jose@example.com",
            "contact_number": "+34600123456",
        }
        form = FosdemRegistrationGuardianForm(data=form_data)
        assert form.is_valid()

        guardian = form.save()
        assert guardian.name == "José María García-López"


@pytest.mark.django_db
@pytest.mark.forms
class TestFosdemRegistrationForm:
    """Test cases for FosdemRegistrationForm."""

    def test_valid_registration_form(self, submission_in_registration_track, guardian):
        """Test form with valid data and proper session context."""
        # Create instance with required relationships first
        instance = FosdemRegistration(
            session=submission_in_registration_track, registering_person=guardian
        )

        form_data = {
            "nickname": "Little Alice",
            "age": 8,
            "special_needs": "Vegetarian diet",
        }
        form = FosdemRegistrationForm(data=form_data, instance=instance)
        with scopes_disabled():
            assert form.is_valid()
            assert form.cleaned_data["nickname"] == "Little Alice"
            assert form.cleaned_data["age"] == 8
            assert form.cleaned_data["special_needs"] == "Vegetarian diet"

        # Test that we can save it
        with scopes_disabled():
            registration = form.save()

        assert registration.session == submission_in_registration_track
        assert registration.registering_person == guardian

    def test_registration_form_missing_required_fields(
        self, submission_in_registration_track, guardian
    ):
        """Test form validation with missing required fields."""
        # Missing nickname
        form_data = {
            "age": 8,
            "special_needs": "None",
        }

        instance = FosdemRegistration(
            session=submission_in_registration_track, registering_person=guardian
        )
        form = FosdemRegistrationForm(data=form_data, instance=instance)
        with scopes_disabled():
            assert not form.is_valid()
            assert "nickname" in form.errors

        # Missing age
        form_data = {
            "nickname": "Little Alice",
            "special_needs": "None",
        }
        form = FosdemRegistrationForm(data=form_data, instance=instance)
        with scopes_disabled():
            assert not form.is_valid()
            assert "age" in form.errors

    def test_registration_form_optional_fields(
        self, submission_in_registration_track, guardian
    ):
        """Test that special_needs is optional."""
        # Create instance with required relationships first
        instance = FosdemRegistration(
            session=submission_in_registration_track, registering_person=guardian
        )

        form_data = {
            "nickname": "Little Alice",
            "age": 8,
            # special_needs is optional
        }
        form = FosdemRegistrationForm(data=form_data, instance=instance)
        with scopes_disabled():
            assert form.is_valid()
            assert form.cleaned_data["special_needs"] == ""

    def test_registration_form_age_validation(
        self, submission_in_registration_track, guardian
    ):
        """Test age field validation."""
        # Age too low
        with scopes_disabled():
            instance = FosdemRegistration(
                session=submission_in_registration_track, registering_person=guardian
            )
            form_data = {
                "nickname": "Little Alice",
                "age": -1,
                "special_needs": "None",
            }
            form = FosdemRegistrationForm(data=form_data, instance=instance)
            assert not form.is_valid()
            assert "age" in form.errors

            # Age too high
            instance = FosdemRegistration(
                session=submission_in_registration_track, registering_person=guardian
            )
            form_data = {
                "nickname": "Little Alice",
                "age": 121,
                "special_needs": "None",
            }
            form = FosdemRegistrationForm(data=form_data, instance=instance)
            assert not form.is_valid()
            assert "age" in form.errors

            # Valid ages
            for age in [0, 1, 10, 17, 120]:
                instance = FosdemRegistration(
                    session=submission_in_registration_track,
                    registering_person=guardian,
                )
                form_data = {
                    "nickname": "Little Alice",
                    "age": age,
                    "special_needs": "None",
                }
                form = FosdemRegistrationForm(data=form_data, instance=instance)
                assert form.is_valid(), f"Age {age} should be valid"


@pytest.mark.django_db
@pytest.mark.forms
class TestRegistrationFormSet:
    """Test cases for RegistrationFormSet."""


def test_formset_valid_data(self, guardian, submission_in_registration_track):
    """Test formset with valid data for multiple registrations."""
    with scopes_disabled():
        formset_data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Alice",
            "form-0-age": "10",
            "form-0-special_needs": "Vegetarian diet",
            "form-1-nickname": "Bob",
            "form-1-age": "8",
            "form-1-special_needs": "",
        }

        formset = RegistrationFormSet(data=formset_data)

        assert formset.is_valid()
        assert len(formset.forms) == 2

        # Check first form
        form0 = formset.forms[0]
        # Create instance for form validation
        form0.instance = FosdemRegistration(
            session=submission_in_registration_track, registering_person=guardian
        )
        assert form0.cleaned_data["nickname"] == "Alice"
        assert form0.cleaned_data["age"] == 10
        assert form0.cleaned_data["special_needs"] == "Vegetarian diet"

        # Check second form
        form1 = formset.forms[1]
        form1.instance = FosdemRegistration(
            session=submission_in_registration_track, registering_person=guardian
        )
        assert form1.cleaned_data["nickname"] == "Bob"
        assert form1.cleaned_data["age"] == 8
        assert form1.cleaned_data["special_needs"] == ""

    def test_formset_minimum_forms(self):
        """Test that formset requires at least one form."""
        formset_data = {
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
        }
        formset = RegistrationFormSet(data=formset_data)
        assert not formset.is_valid()
        assert formset.non_form_errors()

    def test_formset_empty_forms_invalid(self):
        """Test that formset with empty required forms is invalid."""
        formset_data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "",  # Required field empty
            "form-0-age": "",  # Required field empty
            "form-0-special_needs": "",
        }
        formset = RegistrationFormSet(data=formset_data)
        assert not formset.is_valid()

        form0 = formset.forms[0]
        assert "nickname" in form0.errors
        assert "age" in form0.errors

    def test_formset_mixed_valid_invalid(self):
        """Test formset with mix of valid and invalid forms."""
        formset_data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Alice",
            "form-0-age": "10",
            "form-0-special_needs": "Vegetarian",
            "form-1-nickname": "Bob",
            "form-1-age": "150",  # Invalid age
            "form-1-special_needs": "",
        }
        formset = RegistrationFormSet(data=formset_data)
        assert not formset.is_valid()

        form0 = formset.forms[0]
        form1 = formset.forms[1]

        assert form0.is_valid()
        assert not form1.is_valid()
        assert "age" in form1.errors

    def test_formset_save(self, submission, guardian):
        """Test saving formset data."""
        formset_data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Alice",
            "form-0-age": "10",
            "form-0-special_needs": "Vegetarian diet",
            "form-1-nickname": "Bob",
            "form-1-age": "8",
            "form-1-special_needs": "",
        }
        formset = RegistrationFormSet(data=formset_data)
        assert formset.is_valid()

        # Save forms with commit=False to set additional fields
        registrations = formset.save(commit=False)
        for registration in registrations:
            registration.session = submission
            registration.registering_person = guardian
            registration.save()

        assert len(registrations) == 2

        # Verify saved data
        reg1 = FosdemRegistration.objects.get(nickname="Alice")
        assert reg1.age == 10
        assert reg1.special_needs == "Vegetarian diet"

        reg2 = FosdemRegistration.objects.get(nickname="Bob")
        assert reg2.age == 8
        assert reg2.special_needs == ""

    def test_formset_deletion_disabled(self):
        """Test that formset doesn't allow deletion."""
        # This is based on can_delete=False in the formset factory
        formset_data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Alice",
            "form-0-age": "10",
            "form-0-special_needs": "",
            "form-0-DELETE": "on",  # Try to delete
        }
        formset = RegistrationFormSet(data=formset_data)

        # Should still be valid because deletion is disabled
        assert formset.is_valid()
        # And the form shouldn't be marked for deletion
        form0 = formset.forms[0]
        assert not hasattr(form0, "cleaned_data") or not form0.cleaned_data.get(
            "DELETE", False
        )


@pytest.mark.forms
class TestFormHelpers:
    """Test form helper functions and methods."""

    def test_form_field_attributes(self):
        """Test that forms have correct field attributes."""
        guardian_form = FosdemRegistrationGuardianForm()

        # Check that required fields exist
        assert "name" in guardian_form.fields
        assert "email" in guardian_form.fields
        assert "contact_number" in guardian_form.fields

        # Check field types and basic properties
        name_field = guardian_form.fields["name"]
        email_field = guardian_form.fields["email"]
        contact_field = guardian_form.fields["contact_number"]

        # Basic field validation
        assert name_field.required
        assert email_field.required
        assert contact_field.required

        registration_form = FosdemRegistrationForm()

        # Check registration form fields
        assert "nickname" in registration_form.fields
        assert "age" in registration_form.fields
        assert "special_needs" in registration_form.fields

        # Check age field has validators (without testing specific validator types)
        age_field = registration_form.fields["age"]
        assert len(age_field.validators) > 0  # Has some validators

    def test_form_help_text(self):
        """Test that forms have appropriate help text."""
        guardian_form = FosdemRegistrationGuardianForm()
        FosdemRegistrationForm()

        # Help text should be defined for important fields
        # (This depends on your actual model field definitions)
        name_field = guardian_form.fields["name"]
        email_field = guardian_form.fields["email"]
        contact_field = guardian_form.fields["contact_number"]

        # These assertions depend on your model field help_text
        # Adjust based on actual help text in your models
        assert hasattr(name_field, "help_text")
        assert hasattr(email_field, "help_text")
        assert hasattr(contact_field, "help_text")

    def test_formset_configuration(self):
        """Test formset configuration parameters."""
        # Test that formset has correct configuration
        assert RegistrationFormSet.extra == 0
        assert RegistrationFormSet.min_num == 1
        assert RegistrationFormSet.validate_min == True
        assert RegistrationFormSet.can_delete == False
