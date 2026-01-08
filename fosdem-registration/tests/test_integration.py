"""
Integration tests for fosdem_registration plugin.
These tests simulate real user workflows and test components working together.
"""
import pytest
from django.core import mail
from django.test import TransactionTestCase
from django.urls import reverse

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


@pytest.mark.django_db
@pytest.mark.integration
class TestMultipleEventsWorkflow:
    """Test workflow with multiple events to ensure proper isolation."""

    def test_event_isolation(
        self,
        client,
        authenticated_client,
        user_with_permissions,
        submission_type,
        max_participants_question,
        team,
    ):
        """Test that registrations are properly isolated between events."""
        from pretalx.event.models import Event
        from pretalx.submission.models import Submission, Track
        from pretalx.submission.models.question import Answer

        # Create two events
        event1 = Event.objects.create(
            name="FOSDEM 2026",
            slug="fosdem26",
            email="test1@fosdem.org",
            date_from="2026-02-01",
            date_to="2026-02-02",
            timezone="Europe/Brussels",
        )

        event2 = Event.objects.create(
            name="FOSDEM 2027",
            slug="fosdem27",
            email="test2@fosdem.org",
            date_from="2027-02-01",
            date_to="2027-02-02",
            timezone="Europe/Brussels",
        )

        # Create tracks for each event
        track1 = Track.objects.create(name="Kids Track 2026", event=event1)
        track2 = Track.objects.create(name="Kids Track 2027", event=event2)

        # Create submissions for each event
        submission1 = Submission.objects.create(
            title="Workshop 2026",
            code="WORK26",
            event=event1,
            track=track1,
            submission_type=submission_type,
            state="confirmed",
        )

        submission2 = Submission.objects.create(
            title="Workshop 2027",
            code="WORK27",
            event=event2,
            track=track2,
            submission_type=submission_type,
            state="confirmed",
        )

        # Setup registration tracks for each
        reg_track1 = FosdemRegistrationTrack.objects.create(
            track=track1,
            max_number_question=max_participants_question,
        )

        reg_track2 = FosdemRegistrationTrack.objects.create(
            track=track2,
            max_number_question=max_participants_question,
        )

        # Set capacities
        Answer.objects.create(
            submission=submission1,
            question=max_participants_question,
            answer="5",
        )

        Answer.objects.create(
            submission=submission2,
            question=max_participants_question,
            answer="8",
        )

        # Register for event1
        url1 = reverse(
            "plugins:fosdem_registration:register",
            kwargs={"event": event1.slug, "submission_code": submission1.code},
        )

        form_data = {
            "name": "Parent A",
            "email": "parenta@example.com",
            "contact_number": "+32470111111",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Kid A",
            "form-0-age": "8",
            "form-0-special_needs": "",
        }

        response = client.post(url1, data=form_data)
        assert response.status_code == 302

        # Register for event2
        url2 = reverse(
            "plugins:fosdem_registration:register",
            kwargs={"event": event2.slug, "submission_code": submission2.code},
        )

        form_data2 = {
            "name": "Parent B",
            "email": "parentb@example.com",
            "contact_number": "+32470222222",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Kid B",
            "form-0-age": "9",
            "form-0-special_needs": "",
        }

        response = client.post(url2, data=form_data2)
        assert response.status_code == 302

        # Verify event1 overview only shows event1 registrations
        overview_url1 = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event1.slug},
        )

        response = authenticated_client.get(overview_url1)
        submissions = response.context["submissions"]
        assert submissions.count() == 1
        submission_data = submissions.first()
        assert submission_data.title == "Workshop 2026"
        assert submission_data.nr_registrations == 1

        # Verify event2 overview only shows event2 registrations
        overview_url2 = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event2.slug},
        )

        response = authenticated_client.get(overview_url2)
        submissions = response.context["submissions"]
        assert submissions.count() == 1
        submission_data = submissions.first()
        assert submission_data.title == "Workshop 2027"
        assert submission_data.nr_registrations == 1

        # Verify registrations are properly isolated
        registrations1 = FosdemRegistration.objects.filter(session__event=event1)
        registrations2 = FosdemRegistration.objects.filter(session__event=event2)

        assert registrations1.count() == 1
        assert registrations2.count() == 1
        assert registrations1.first().nickname == "Kid A"
        assert registrations2.first().nickname == "Kid B"


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceAndScale:
    """Test performance with larger datasets."""

    def test_bulk_registration_handling(
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
        """Test handling of bulk registrations efficiently."""
        from pretalx.submission.models import Submission
        from pretalx.submission.models.question import Answer

        # Create submission with high capacity
        submission = Submission.objects.create(
            title="Large Workshop",
            code="LARGE1",
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
            answer="100",
        )

        registration_url = reverse(
            "plugins:fosdem_registration:register",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        # Create multiple registrations
        import time

        start_time = time.time()

        for i in range(10):  # Create 10 families with 2 kids each = 20 registrations
            form_data = {
                "name": f"Family {i}",
                "email": f"family{i}@example.com",
                "contact_number": f"+3247012{i:04d}",
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "0",
                "form-MIN_NUM_FORMS": "1",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-nickname": f"Kid{i}A",
                "form-0-age": str(8 + (i % 5)),
                "form-0-special_needs": "",
                "form-1-nickname": f"Kid{i}B",
                "form-1-age": str(9 + (i % 4)),
                "form-1-special_needs": "",
            }

            response = client.post(registration_url, data=form_data)
            assert response.status_code == 302

        registration_time = time.time() - start_time

        # Should complete reasonably quickly (adjust threshold as needed)
        assert registration_time < 10.0  # 10 seconds for 20 registrations

        # Verify all registrations were created
        assert FosdemRegistration.objects.count() == 20
        assert FosdemRegistrationGuardian.objects.count() == 10

        # Test overview performance
        overview_url = reverse(
            "plugins:fosdem_registration:overview",
            kwargs={"event": event.slug},
        )

        start_time = time.time()
        response = authenticated_client.get(overview_url)
        overview_time = time.time() - start_time

        assert response.status_code == 200
        assert overview_time < 2.0  # Should be fast with proper queries

        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 20

        # Test detail view performance
        detail_url = reverse(
            "plugins:fosdem_registration:detail",
            kwargs={
                "event": event.slug,
                "submission_code": submission.code,
            },
        )

        start_time = time.time()
        response = authenticated_client.get(detail_url)
        detail_time = time.time() - start_time

        assert response.status_code == 200
        assert detail_time < 2.0  # Should be fast with proper queries

        registrations_list = response.context["object_list"]
        assert registrations_list.count() == 20
