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
from django_scopes import scope, scopes_disabled

# Import pretalx models
from pretalx.event.models import Event, Organiser, Team
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
def event(organiser):
    """Create a test event."""
    event = Event(
        name="Test FOSDEM",
        slug="test-fosdem",
        email="test@example.org",
        date_from=date(2026, 2, 1),
        date_to=date(2026, 2, 2),
        timezone="Europe/Brussels",
        organiser=organiser,
        is_public=True,
        custom_domain=None,  # Explicitly set to None for testing
    )

    with scope(event=event):
        event.save()
    return event


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
def organiser():
    o = Organiser.objects.create(name="Test Organiser", slug="testorganiser")
    return o


@pytest.fixture
def team(user, organiser):
    """Create a test team with user."""
    team = Team.objects.create(
        name="Test Team",
        can_change_submissions=True,
        can_change_organiser_settings=True,
        organiser=organiser,
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
    with scope(event=event):
        track = Track.objects.create(
            name="Kids Track",
            event=event,
            color="#ff0000",
        )
    return track


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
    submission = Submission.objects.create(
        title="Test Workshop for Kids",
        abstract="A fun workshop for children",
        description="Learn programming in a fun way",
        code="TESTKIDS1",
        event=event,
        track=track,
        submission_type=submission_type,
        state="confirmed",
    )
    return submission


@pytest.fixture
def submission_in_registration_track(
    event, submission_type, registration_track, max_participants_question
):
    """Create a test submission linked to a registration track."""
    submission = Submission.objects.create(
        title="Test Workshop with Registration",
        abstract="A fun workshop requiring registration",
        description="Learn programming in a fun way with limited seats",
        code="TESTKIDS2",
        event=event,
        track=registration_track.track,
        submission_type=submission_type,
        state="confirmed",
    )
    Answer.objects.create(
        submission=submission,
        question=max_participants_question,
        answer="5",
    )
    return submission


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
@scopes_disabled()
def multiple_registrations(submission_in_registration_track, guardian):
    """Create multiple test registrations for capacity testing."""
    registrations = []
    for i in range(5):
        reg = FosdemRegistration.objects.create(
            session=submission_in_registration_track,
            registering_person=guardian,
            nickname=f"Test Kid {i+1}",
            age=7 + i,
            special_needs="None",
        )
        registrations.append(reg)
    return registrations


@pytest.fixture
def user_with_permissions(user, registration_track, team, event):
    """Create a user with necessary permissions."""
    # Add permission to view registrations
    registration_track.teams.add(team)
    team.organiser = event.organiser
    team.members.add(user)
    team.save()
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
@scopes_disabled()
def registration_talkslot(submission_in_registration_track):
    """Create a talk slot for the submission in registration track."""
    from pretalx.schedule.models import TalkSlot

    event = submission_in_registration_track.event
    talkslot = TalkSlot.objects.create(
        submission=submission_in_registration_track,
        is_visible=True,
        start=event.date_from,
        end=event.date_from,
        schedule=event.wip_schedule,
    )
    event.release_schedule(name="first schedule")

    return talkslot


@pytest.fixture
def registration_url(registration_talkslot):
    """URL for registration form."""
    event = registration_talkslot.submission.event
    # Ensure event is public
    event.is_public = True
    event.save()

    return reverse(
        "plugins:fosdem_registration:register_person",
        kwargs={
            "event": event.slug,
            "submission_code": registration_talkslot.submission.code,
        },
    )


@pytest.fixture
def overview_url(event):
    """URL for registration overview."""
    return reverse(
        "plugins:fosdem_registration:registration_overview",
        kwargs={"event": event.slug},
    )


@pytest.fixture
def detail_url(event, submission_in_registration_track):
    """URL for registration detail view."""
    return reverse(
        "plugins:fosdem_registration:registration_detail",
        kwargs={
            "event": event.slug,
            "submission_code": submission_in_registration_track.code,
        },
    )
