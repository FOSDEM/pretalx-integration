"""
Unit tests for fosdem_registration models.
"""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

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

    def test_create_registration(self, submission, guardian):
        """Test creating a registration."""
        registration = FosdemRegistration.objects.create(
            session=submission,
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

    def test_registration_default_values(self, submission, guardian):
        """Test default values for registration."""
        registration = FosdemRegistration.objects.create(
            session=submission,
            registering_person=guardian,
            nickname="Test Kid",
            age=8,
        )

        assert registration.special_needs == ""
        assert not registration.removed

    def test_age_validation_min(self, submission, guardian):
        """Test minimum age validation."""
        with pytest.raises(ValidationError):
            registration = FosdemRegistration(
                session=submission,
                registering_person=guardian,
                nickname="Test Kid",
                age=-1,  # Invalid age
            )
            registration.full_clean()

    def test_age_validation_max(self, submission, guardian):
        """Test maximum age validation."""
        with pytest.raises(ValidationError):
            registration = FosdemRegistration(
                session=submission,
                registering_person=guardian,
                nickname="Test Kid",
                age=121,  # Invalid age
            )
            registration.full_clean()

    def test_age_validation_valid_range(self, submission, guardian):
        """Test valid age range."""
        registration = FosdemRegistration(
            session=submission,
            registering_person=guardian,
            nickname="Test Kid",
            age=10,
        )
        # Should not raise
        registration.full_clean()

    def test_capacity_validation_success(
        self, submission, guardian, registration_track, max_participants_answer
    ):
        """Test successful registration within capacity."""
        registration = FosdemRegistration(
            session=submission,
            registering_person=guardian,
            nickname="Test Kid",
            age=8,
        )

        # Should not raise ValidationError
        registration.clean()

    def test_capacity_validation_failure(
        self,
        submission,
        guardian,
        registration_track,
        max_participants_answer,
        multiple_registrations,
    ):
        """Test registration failure when capacity is exceeded."""
        # multiple_registrations fixture creates 5 registrations
        # max_participants_answer sets limit to 10

        # Create 6 more registrations to exceed capacity
        for i in range(6):
            FosdemRegistration.objects.create(
                session=submission,
                registering_person=guardian,
                nickname=f"Extra Kid {i}",
                age=8,
            )

        # This should exceed the limit of 10
        with pytest.raises(ValidationError) as exc_info:
            registration = FosdemRegistration(
                session=submission,
                registering_person=guardian,
                nickname="Over Limit Kid",
                age=8,
            )
            registration.clean()

        assert "Registration limit" in str(exc_info.value)

    def test_removed_registration(self, registration):
        """Test removing a registration."""
        assert not registration.removed

        registration.removed = True
        registration.save()

        assert registration.removed

    def test_registration_without_track_setup(self, submission, guardian):
        """Test registration for submission without registration track."""
        # Remove the track from registration tracks
        if hasattr(submission.track, "fosdemregistrationtrack"):
            submission.track.fosdemregistrationtrack.delete()

        registration = FosdemRegistration(
            session=submission,
            registering_person=guardian,
            nickname="Test Kid",
            age=8,
        )

        # Should not raise error when track is not in registration system
        registration.clean()

    def test_save_calls_clean(
        self,
        submission,
        guardian,
        registration_track,
        max_participants_answer,
        multiple_registrations,
    ):
        """Test that save() method calls clean() for validation."""
        # Add enough registrations to exceed limit
        for i in range(6):
            FosdemRegistration.objects.create(
                session=submission,
                registering_person=guardian,
                nickname=f"Extra Kid {i}",
                age=8,
            )

        # This should fail because save() calls clean()
        with pytest.raises(ValidationError):
            registration = FosdemRegistration(
                session=submission,
                registering_person=guardian,
                nickname="Over Limit Kid",
                age=8,
            )
            registration.save()


@pytest.mark.django_db
@pytest.mark.models
class TestModelRelationships:
    """Test relationships between models."""

    def test_guardian_registrations_relationship(self, registration):
        """Test reverse relationship from guardian to registrations."""
        guardian = registration.registering_person

        assert registration in guardian.fosdemregistration_set.all()

    def test_submission_registrations_relationship(self, registration):
        """Test reverse relationship from submission to registrations."""
        submission = registration.session

        assert registration in submission.fosdemregistration_set.all()

    def test_cascade_deletion_guardian(self, registration):
        """Test that deleting guardian deletes registrations."""
        guardian = registration.registering_person
        registration_id = registration.pk

        guardian.delete()

        assert not FosdemRegistration.objects.filter(pk=registration_id).exists()

    def test_cascade_deletion_submission(self, registration):
        """Test that deleting submission deletes registrations."""
        submission = registration.session
        registration_id = registration.pk

        submission.delete()

        assert not FosdemRegistration.objects.filter(pk=registration_id).exists()

    def test_cascade_deletion_track(self, registration_track):
        """Test that deleting track deletes registration track."""
        track = registration_track.track
        reg_track_id = registration_track.pk

        track.delete()

        assert not FosdemRegistrationTrack.objects.filter(pk=reg_track_id).exists()
