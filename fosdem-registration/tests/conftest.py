"""
Test configuration and fixtures for fosdem_registration tests.

Make sure to run these tests from your pretalx environment with:
    python -m pytest
"""
import os
from datetime import date

import pytest

# Set Django settings if not already set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")

# Import Django first
import django
from django.conf import settings

# Setup Django if needed
if not settings.configured:
    django.setup()

from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse

# Import pretalx models
from pretalx.event.models import Event, Team
from pretalx.person.models import User
from pretalx.submission.models import Question, Submission, SubmissionType, Track
from pretalx.submission.models.question import Answer

# Import plugin models
from fosdem_registration.models import (
    FosdemRegistration,
    FosdemRegistrationGuardian,
    FosdemRegistrationTrack,
)


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def event():
    """Create a test event."""
    return Event.objects.create(
        name="Test FOSDEM",
        slug="test-fosdem",
        email="test@example.org",
        date_from=date(2026, 2, 1),
        date_to=date(2026, 2, 2),
        timezone="Europe/Brussels",
    )


@pytest.fixture
def user(event):
    """Create a test user."""
    return User.objects.create_user(
        email="testuser@example.com",
        name="Test User",
        nick="testuser",
        password="testpass123",
    )


@pytest.fixture
def team(event, user):
    """Create a test team with user."""
    team = Team.objects.create(
        event=event,
        name="Test Team",
        can_change_submissions=True,
        can_change_organizer_settings=True,
    )
    team.members.add(user)
    return team


@pytest.fixture
def submission_type(event):
    """Create a submission type."""
    return SubmissionType.objects.create(
        name="Workshop",
        event=event,
        default_duration=60,
    )


@pytest.fixture
def track(event):
    """Create a test track."""
    return Track.objects.create(
        name="Kids Track",
        event=event,
        color="#ff0000",
    )


@pytest.fixture
def max_participants_question(event):
    """Create a question for maximum participants."""
    return Question.objects.create(
        event=event,
        question={"en": "Maximum number of participants"},
        target="submission",
        variant="number",
    )


@pytest.fixture
def registration_track(track, max_participants_question, team):
    """Create a fosdem registration track."""
    reg_track = FosdemRegistrationTrack.objects.create(
        track=track,
        max_number_question=max_participants_question,
    )
    reg_track.teams.add(team)
    return reg_track


@pytest.fixture
def submission(event, track, submission_type, user):
    """Create a test submission."""
    return Submission.objects.create(
        title="Test Workshop for Kids",
        abstract="A fun workshop for children",
        description="Learn programming in a fun way",
        code="TESTKIDS1",
        event=event,
        track=track,
        submission_type=submission_type,
        state="confirmed",
    )


@pytest.fixture
def max_participants_answer(submission, max_participants_question):
    """Create an answer for maximum participants."""
    return Answer.objects.create(
        submission=submission,
        question=max_participants_question,
        answer="10",
    )


@pytest.fixture
def guardian():
    """Create a test guardian."""
    return FosdemRegistrationGuardian.objects.create(
        name="Test Parent",
        email="parent@example.com",
        contact_number="+32470123456",
    )


@pytest.fixture
def registration(submission, guardian):
    """Create a test registration."""
    return FosdemRegistration.objects.create(
        session=submission,
        registering_person=guardian,
        nickname="Test Kid",
        age=8,
        special_needs="None",
    )


@pytest.fixture
def multiple_registrations(submission, guardian):
    """Create multiple test registrations for capacity testing."""
    registrations = []
    for i in range(5):
        reg = FosdemRegistration.objects.create(
            session=submission,
            registering_person=guardian,
            nickname=f"Test Kid {i+1}",
            age=7 + i,
            special_needs="None",
        )
        registrations.append(reg)
    return registrations


@pytest.fixture
def user_with_permissions(user, event):
    """Create a user with necessary permissions."""
    # Add permission to view registrations
    permission = Permission.objects.get_or_create(
        codename="view_fosdem_registrations",
        name="Can view fosdem registrations",
        content_type_id=1,  # This might need adjustment based on your setup
    )[0]
    user.user_permissions.add(permission)
    return user


@pytest.fixture
def authenticated_client(client, user_with_permissions):
    """Client with authenticated user."""
    client.force_login(user_with_permissions)
    return client


@pytest.fixture
def sample_form_data():
    """Sample form data for registration."""
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "contact_number": "+32470987654",
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


@pytest.fixture
def registration_url(event, submission):
    """URL for registration form."""
    return reverse(
        "plugins:fosdem_registration:register",
        kwargs={
            "event": event.slug,
            "submission_code": submission.code,
        },
    )


@pytest.fixture
def overview_url(event):
    """URL for registration overview."""
    return reverse(
        "plugins:fosdem_registration:overview",
        kwargs={"event": event.slug},
    )


@pytest.fixture
def detail_url(event, submission):
    """URL for registration detail view."""
    return reverse(
        "plugins:fosdem_registration:detail",
        kwargs={
            "event": event.slug,
            "submission_code": submission.code,
        },
    )
