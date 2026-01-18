"""
Unit tests for fosdem_registration models.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django_scopes import scopes_disabled

from fosdem_registration.models import (
    FosdemRegistration,
    FosdemRegistrationGuardian,
    FosdemRegistrationTrack,
)


@pytest.mark.django_db
@pytest.mark.models
class TestFosdemRegistrationGuardian:
    """Test cases for FosdemRegistrationGuardian model."""

    def test_create_guardian(self):
        """Test creating a guardian."""
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Test Parent",
            email="parent@example.com",
            contact_number="+32470123456",
        )

        assert guardian.name == "Test Parent"
        assert guardian.email == "parent@example.com"
        assert guardian.contact_number == "+32470123456"
        assert str(guardian.pk)  # Has a primary key

    def test_guardian_email_validation(self):
        """Test email field validation."""
        with pytest.raises(ValidationError):
            guardian = FosdemRegistrationGuardian(
                name="Test Parent",
                email="invalid-email",
                contact_number="+32470123456",
            )
            guardian.full_clean()

    def test_guardian_required_fields(self):
        """Test that required fields cannot be empty."""
        with pytest.raises(ValidationError):
            guardian = FosdemRegistrationGuardian(
                name="",  # Required field
                email="parent@example.com",
                contact_number="+32470123456",
            )
            guardian.full_clean()


@pytest.mark.django_db
@pytest.mark.models
class TestFosdemRegistrationTrack:
    """Test cases for FosdemRegistrationTrack model."""

    def test_create_registration_track(self, track, max_participants_question):
        """Test creating a registration track."""
        reg_track = FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )

        assert reg_track.track == track
        assert reg_track.max_number_question == max_participants_question
        assert reg_track.pk is not None

    def test_track_teams_relationship(self, registration_track, team):
        """Test many-to-many relationship with teams."""
        registration_track.teams.add(team)

        assert team in registration_track.teams.all()
        assert registration_track in team.fosdemregistrationtrack_set.all()

    def test_one_to_one_track_constraint(self, track, max_participants_question):
        """Test that each track can only have one registration track."""
        FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )

        with pytest.raises(IntegrityError):
            FosdemRegistrationTrack.objects.create(
                track=track,  # Same track
                max_number_question=max_participants_question,
            )


@pytest.mark.django_db
@pytest.mark.models
class TestFosdemRegistration:
    """Test cases for FosdemRegistration model."""

    def test_create_registration(
        self, submission_in_registration_track, guardian, max_participants_answer
    ):
        """Test creating a registration."""
        submission = submission_in_registration_track
        with scopes_disabled():
            registration = FosdemRegistration.objects.create(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=8,
                special_needs="Vegetarian diet",
            )

        assert registration.session == submission
        assert registration.registering_person == guardian
        assert registration.nickname == "Test Kid"
        assert registration.age == 8
        assert registration.special_needs == "Vegetarian diet"
        assert not registration.removed

    def test_registration_default_values(
        self, submission_in_registration_track, guardian
    ):
        """Test default values for registration."""
        with scopes_disabled():
            registration = FosdemRegistration.objects.create(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=8,
            )

        assert registration.special_needs == ""
        assert not registration.removed

    def test_age_validation_min(self, submission_in_registration_track, guardian):
        """Test minimum age validation."""
        with pytest.raises(ValidationError), scopes_disabled():
            registration = FosdemRegistration(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=-1,  # Invalid age
            )
            registration.full_clean()

    def test_age_validation_max(self, submission_in_registration_track, guardian):
        """Test maximum age validation."""
        with pytest.raises(ValidationError), scopes_disabled():
            registration = FosdemRegistration(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=121,  # Invalid age
            )
            registration.full_clean()

    def test_age_validation_valid_range(
        self, submission_in_registration_track, guardian
    ):
        """Test valid age range."""
        with scopes_disabled():
            registration = FosdemRegistration(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=10,
            )
            # Should not raise
            registration.full_clean()

    def test_capacity_validation_success(
        self, submission_in_registration_track, guardian
    ):
        """Test successful registration within capacity."""
        with scopes_disabled():
            registration = FosdemRegistration(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="Test Kid",
                age=8,
            )

            # Should not raise ValidationError
            registration.clean()

    def test_capacity_validation_failure(
        self, submission_in_registration_track, guardian
    ):
        """Test registration failure when capacity is exceeded."""
        # multiple_registrations fixture creates 5 registrations
        # max_participants_answer sets limit to 10

        # Create 6 more registrations to exceed capacity
        with scopes_disabled():
            for i in range(5):
                FosdemRegistration.objects.create(
                    session=submission_in_registration_track,
                    registering_person=guardian,
                    nickname=f"Extra Kid {i}",
                    age=8,
                )

            # This should exceed the limit of 5
            with pytest.raises(ValidationError) as exc_info:
                registration = FosdemRegistration(
                    session=submission_in_registration_track,
                    registering_person=guardian,
                    nickname="Over Limit Kid",
                    age=8,
                )
                registration.clean()

            assert "Registration limit" in str(exc_info.value)

    def test_capacity_validation_excludes_removed(
        self, submission_in_registration_track, guardian
    ):
        """Test that removed registrations don't count toward capacity."""
        # max_participants_answer sets limit to 10

        # Create 4 active registrations
        with scopes_disabled():
            for i in range(4):
                FosdemRegistration.objects.create(
                    session=submission_in_registration_track,
                    registering_person=guardian,
                    nickname=f"Active Kid {i}",
                    age=8,
                )

            # Create 3 removed registrations
            for i in range(3):
                FosdemRegistration.objects.create(
                    session=submission_in_registration_track,
                    registering_person=guardian,
                    nickname=f"Removed Kid {i}",
                    age=8,
                    removed=True,
                )

            # Should be able to add one more since removed don't count
            registration = FosdemRegistration(
                session=submission_in_registration_track,
                registering_person=guardian,
                nickname="New Kid",
                age=8,
            )
            # Should not raise ValidationError
            registration.clean()
