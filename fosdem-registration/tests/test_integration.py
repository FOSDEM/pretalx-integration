"""
Integration tests for fosdem_registration plugin.
These tests simulate real user workflows and test components working together.
"""

import pytest
from django.core import mail
from django.test import TransactionTestCase
from django.urls import reverse
from django_scopes import scope, scopes_disabled

from fosdem_registration.models import (
    FosdemRegistration,
    FosdemRegistrationGuardian,
    FosdemRegistrationTrack,
)


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestCompleteRegistrationWorkflow:
    """Test complete registration workflow from start to finish."""

    def test_full_registration_workflow(
        self,
        client,
        authenticated_client,
        event,
        track,
        submission_type,
        max_participants_question,
        team,
        user_with_permissions,
    ):
        """Test complete workflow: setup -> register -> view -> manage."""

        # 1. Setup: Create submission and registration track
        from pretalx.submission.models import Submission
        from pretalx.submission.models.question import Answer

        submission = Submission.objects.create(
            title="Kids Python Workshop",
            abstract="Learn Python programming for kids",
            description="A hands-on workshop teaching Python basics to children",
            code="KIDSWORK1",
            event=event,
            track=track,
            submission_type=submission_type,
            state="confirmed",
        )

        # Create registration track
        reg_track = FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )
        reg_track.teams.add(team)

        # Set maximum participants
        Answer.objects.create(
            submission=submission,
            question=max_participants_question,
            answer="15",
        )

        # 2. Public registration
        registration_url = reverse(
            "plugins:fosdem_registration:register",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        # Get registration form
        response = client.get(registration_url)
        assert response.status_code == 200
        assert "Kids Python Workshop" in response.content.decode()

        # Submit registration
        form_data = {
            "name": "Sarah Johnson",
            "email": "sarah@example.com",
            "contact_number": "+32470555666",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Emma",
            "form-0-age": "9",
            "form-0-special_needs": "Vegetarian meal",
            "form-1-nickname": "Jake",
            "form-1-age": "11",
            "form-1-special_needs": "",
        }

        response = client.post(registration_url, data=form_data)
        assert response.status_code == 302  # Redirect after successful registration

        # Verify registration data was saved
        guardian = FosdemRegistrationGuardian.objects.get(email="sarah@example.com")
        assert guardian.name == "Sarah Johnson"

        registrations = FosdemRegistration.objects.filter(registering_person=guardian)
        assert registrations.count() == 2

        emma = registrations.get(nickname="Emma")
        assert emma.age == 9
        assert emma.special_needs == "Vegetarian meal"

        jake = registrations.get(nickname="Jake")
        assert jake.age == 11
        assert jake.special_needs == ""

        # 3. Organizer views registrations
        overview_url = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event.slug},
        )

        response = authenticated_client.get(overview_url)
        assert response.status_code == 200

        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.title == "Kids Python Workshop"
        assert submission_data.nr_registrations == 2
        assert submission_data.max_number == "15"

        # 4. Organizer views registration details
        detail_url = reverse(
            "plugins:fosdem_registration:detail",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        response = authenticated_client.get(detail_url)
        assert response.status_code == 200

        registrations_list = response.context["object_list"]
        assert registrations_list.count() == 2

        submission_context = response.context["submission"]
        assert submission_context.title == "Kids Python Workshop"

    def test_capacity_management_workflow(
        self,
        client,
        authenticated_client,
        event,
        track,
        submission_type,
        max_participants_question,
        team,
        user_with_permissions,
    ):
        """Test workflow when registration reaches capacity limits."""

        # Setup submission with low capacity
        from pretalx.submission.models import Submission
        from pretalx.submission.models.question import Answer

        submission = Submission.objects.create(
            title="Small Workshop",
            abstract="Limited capacity workshop",
            code="SMALL1",
            event=event,
            track=track,
            submission_type=submission_type,
            state="confirmed",
        )

        reg_track = FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )
        reg_track.teams.add(team)

        # Set very low capacity
        Answer.objects.create(
            submission=submission,
            question=max_participants_question,
            answer="3",
        )

        registration_url = reverse(
            "plugins:fosdem_registration:register",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        # First registration (2 kids) - should succeed
        form_data = {
            "name": "Parent One",
            "email": "parent1@example.com",
            "contact_number": "+32470111111",
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Kid1",
            "form-0-age": "8",
            "form-0-special_needs": "",
            "form-1-nickname": "Kid2",
            "form-1-age": "10",
            "form-1-special_needs": "",
        }

        response = client.post(registration_url, data=form_data)
        assert response.status_code == 302
        assert FosdemRegistration.objects.count() == 2

        # Check overview shows 2/3 capacity used
        overview_url = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event.slug},
        )

        response = authenticated_client.get(overview_url)
        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 2
        assert submission_data.max_number == "3"

        # Second registration (1 kid) - should succeed and fill capacity
        form_data2 = {
            "name": "Parent Two",
            "email": "parent2@example.com",
            "contact_number": "+32470222222",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Kid3",
            "form-0-age": "9",
            "form-0-special_needs": "",
        }

        response = client.post(registration_url, data=form_data2)
        assert response.status_code == 302
        assert FosdemRegistration.objects.count() == 3

        # Third registration attempt - should fail
        form_data3 = {
            "name": "Parent Three",
            "email": "parent3@example.com",
            "contact_number": "+32470333333",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Kid4",
            "form-0-age": "7",
            "form-0-special_needs": "",
        }

        response = client.post(registration_url, data=form_data3)
        assert response.status_code == 200  # Form redisplayed with errors
        assert FosdemRegistration.objects.count() == 3  # No new registration

        # Should show capacity error
        content = response.content.decode().lower()
        assert "limit" in content or "full" in content or "capacity" in content

        # Final overview check - should show full capacity
        response = authenticated_client.get(overview_url)
        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 3
        assert submission_data.max_number == "3"

    def test_capacity_limits_with_removed_registrations(
        self,
        client,
        authenticated_client,
        event,
        track,
        submission_type,
        max_participants_question,
        team,
        user_with_permissions,
    ):
        """Test that removed registrations don't count toward capacity."""
        from pretalx.submission.models import Submission
        from pretalx.submission.models.question import Answer

        submission = Submission.objects.create(
            title="Workshop with Removals",
            abstract="Testing removed registrations",
            code="REMOV1",
            event=event,
            track=track,
            submission_type=submission_type,
            state="confirmed",
        )

        reg_track = FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )
        reg_track.teams.add(team)

        # Set capacity to 3
        Answer.objects.create(
            submission=submission,
            question=max_participants_question,
            answer="3",
        )

        # Create guardian
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Test Parent",
            email="parent@example.com",
            contact_number="+32470111111",
        )

        # Create 2 active and 2 removed registrations
        for i in range(2):
            FosdemRegistration.objects.create(
                session=submission,
                registering_person=guardian,
                nickname=f"Active Kid {i}",
                age=8,
            )

        for i in range(2):
            FosdemRegistration.objects.create(
                session=submission,
                registering_person=guardian,
                nickname=f"Removed Kid {i}",
                age=8,
                removed=True,
            )

        # Overview should show 2 registrations (not 4)
        overview_url = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event.slug},
        )
        response = authenticated_client.get(overview_url)
        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 2

        # Should be able to add 1 more (3 total active)
        registration_url = reverse(
            "plugins:fosdem_registration:register",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        form_data = {
            "name": "New Parent",
            "email": "newparent@example.com",
            "contact_number": "+32470222222",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "New Kid",
            "form-0-age": "8",
            "form-0-special_needs": "",
        }

        response = client.post(registration_url, data=form_data)
        assert response.status_code == 302  # Should succeed
        assert FosdemRegistration.objects.filter(removed=False).count() == 3

    def test_email_notification_workflow(
        self, client, event, track, submission_type, max_participants_question, team
    ):
        """Test email notifications are sent during registration."""
        # Setup
        from pretalx.submission.models import Submission
        from pretalx.submission.models.question import Answer

        submission = Submission.objects.create(
            title="Test Workshop",
            code="EMAIL1",
            event=event,
            track=track,
            submission_type=submission_type,
            state="confirmed",
        )

        reg_track = FosdemRegistrationTrack.objects.create(
            track=track,
            max_number_question=max_participants_question,
        )

        Answer.objects.create(
            submission=submission,
            question=max_participants_question,
            answer="10",
        )

        registration_url = reverse(
            "plugins:fosdem_registration:register",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        # Clear any existing mail
        mail.outbox = []

        # Register
        form_data = {
            "name": "Test Parent",
            "email": "test@example.com",
            "contact_number": "+32470123456",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Test Kid",
            "form-0-age": "8",
            "form-0-special_needs": "",
        }

        response = client.post(registration_url, data=form_data)
        assert response.status_code == 302

        # Check email was sent
        assert len(mail.outbox) >= 1

        confirmation_email = mail.outbox[0]
        assert "test@example.com" in confirmation_email.to
        assert "registration" in confirmation_email.subject.lower()
        assert "Test Workshop" in confirmation_email.body
        assert "Test Kid" in confirmation_email.body
