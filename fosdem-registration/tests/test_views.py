"""
Unit tests for fosdem_registration views.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from django.urls import reverse
from django_scopes import scopes_disabled

from fosdem_registration.models import FosdemRegistration, FosdemRegistrationGuardian
from fosdem_registration.views import (
    GuardianWithRegistrationsCreateView,
    RegistrationDetail,
    RegistrationOverview,
)


@pytest.mark.django_db
@pytest.mark.views
class TestRegistrationOverview:
    """Test cases for RegistrationOverview view."""

    def test_overview_requires_permission(self, client, overview_url):
        """Test that overview view requires proper permissions."""
        response = client.get(overview_url)
        # Should redirect to login or return 403
        assert response.status_code in [302, 403]

    def test_overview_with_authenticated_user(
        self,
        authenticated_client,
        overview_url,
        registration_track,
        submission,
        max_participants_answer,
    ):
        """Test overview with authenticated user having permissions."""
        with scopes_disabled():
            response = authenticated_client.get(overview_url)
            assert response.status_code == 200
            assert "submissions" in response.context

    @scopes_disabled()
    def test_overview_queryset_filtering(
        self,
        event,
        registration_track,
        submission,
        max_participants_answer,
        user_with_permissions,
    ):
        """Test that overview only shows submissions with registration tracks."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user_with_permissions
        request.event = event

        view = RegistrationOverview()
        view.request = request
        view.kwargs = {"event": event.slug}

        queryset = view.get_queryset()

        assert submission in queryset
        # Verify annotations
        submission_data = queryset.first()
        assert hasattr(submission_data, "nr_registrations")
        assert hasattr(submission_data, "max_number")

    @scopes_disabled()
    def test_overview_registration_counts(
        self,
        authenticated_client,
        overview_url,
        registration_track,
        submission,
        max_participants_answer,
        multiple_registrations,
    ):
        """Test that overview shows correct registration counts."""
        response = authenticated_client.get(overview_url)
        assert response.status_code == 200

        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert (
            submission_data.nr_registrations == 5
        )  # from multiple_registrations fixture


@pytest.mark.django_db
@pytest.mark.views
class TestRegistrationDetail:
    """Test cases for RegistrationDetail view."""

    def test_detail_requires_permission(self, client, detail_url):
        """Test that detail view requires proper permissions."""
        response = client.get(detail_url)
        assert response.status_code in [302, 403]

    def test_detail_with_authenticated_user(
        self,
        authenticated_client,
        detail_url,
        registration_track,
        submission,
        registration,
    ):
        """Test detail view with authenticated user."""
        response = authenticated_client.get(detail_url)
        assert response.status_code == 200
        assert "object_list" in response.context
        assert "submission" in response.context
        assert "talkslot" in response.context

    def test_detail_shows_registrations(
        self,
        authenticated_client,
        detail_url,
        registration_track,
        submission,
        multiple_registrations,
    ):
        """Test that detail view shows all registrations for a session."""
        response = authenticated_client.get(detail_url)
        assert response.status_code == 200

        registrations = response.context["object_list"]
        assert registrations.count() == 5

    def test_detail_invalid_submission(self, authenticated_client, event):
        """Test detail view with invalid submission code."""
        invalid_url = reverse(
            "plugins:fosdem_registration:registration_detail",
            kwargs={
                "event": event.slug,
                "submission_code": "INVALID",
            },
        )
        response = authenticated_client.get(invalid_url)
        assert response.status_code == 404

    def test_detail_context_data(
        self, event, submission, registration_track, user_with_permissions
    ):
        """Test context data in detail view."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user_with_permissions
        request.event = event

        view = RegistrationDetail()
        view.request = request
        view.kwargs = {
            "event": event.slug,
            "submission_code": submission.code,
        }

        context = view.get_context_data()

        assert "submission" in context
        assert context["submission"] == submission


@pytest.mark.django_db
@pytest.mark.views
class TestGuardianWithRegistrationsCreateView:
    """Test cases for GuardianWithRegistrationsCreateView."""

    def test_registration_form_get(self, client, registration_url, registration_track):
        """Test GET request to registration form."""
        response = client.get(registration_url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_registration_form_context(
        self,
        client,
        registration_url,
        registration_track,
        submission,
        max_participants_answer,
    ):
        """Test context data in registration form."""
        response = client.get(registration_url)
        assert response.status_code == 200

        context = response.context
        assert "submissions" in context
        # Should contain submissions for registration tracks
        submissions = context["submissions"]
        assert submission in submissions

    def test_registration_form_post_valid(
        self,
        client,
        registration_url,
        registration_track,
        submission,
        max_participants_answer,
        sample_form_data,
    ):
        """Test POST request with valid data."""
        initial_guardian_count = FosdemRegistrationGuardian.objects.count()
        initial_registration_count = FosdemRegistration.objects.count()

        response = client.post(registration_url, data=sample_form_data)

        # Should redirect on success
        assert response.status_code == 302

        # Should create guardian and registrations
        assert FosdemRegistrationGuardian.objects.count() == initial_guardian_count + 1
        assert FosdemRegistration.objects.count() == initial_registration_count + 2

        # Check created data
        guardian = FosdemRegistrationGuardian.objects.latest("id")
        assert guardian.name == "Jane Doe"
        assert guardian.email == "jane.doe@example.com"

        registrations = FosdemRegistration.objects.filter(registering_person=guardian)
        assert registrations.count() == 2

        reg1, reg2 = registrations.order_by("id")
        assert reg1.nickname == "Alice"
        assert reg1.age == 10
        assert reg2.nickname == "Bob"
        assert reg2.age == 8

    def test_registration_form_post_invalid_guardian(
        self, client, registration_url, registration_track, sample_form_data
    ):
        """Test POST request with invalid guardian data."""
        invalid_data = sample_form_data.copy()
        invalid_data["email"] = "invalid-email"

        response = client.post(registration_url, data=invalid_data)

        # Should not redirect, should show form with errors
        assert response.status_code == 200
        assert "form" in response.context
        # Should not create any objects
        assert not FosdemRegistrationGuardian.objects.filter(name="Jane Doe").exists()

    def test_registration_form_post_invalid_age(
        self, client, registration_url, registration_track, sample_form_data
    ):
        """Test POST request with invalid age."""
        invalid_data = sample_form_data.copy()
        invalid_data["form-0-age"] = "150"  # Invalid age

        response = client.post(registration_url, data=invalid_data)

        # Should not redirect, should show form with errors
        assert response.status_code == 200
        assert not FosdemRegistrationGuardian.objects.filter(name="Jane Doe").exists()

    def test_registration_capacity_check(
        self,
        client,
        registration_url,
        registration_track,
        submission,
        max_participants_answer,
        multiple_registrations,  # Creates 5 registrations
        sample_form_data,
    ):
        """Test registration when approaching capacity limit."""
        # max_participants_answer sets limit to 10
        # multiple_registrations creates 5 registrations
        # sample_form_data tries to add 2 more = 7 total (should work)

        response = client.post(registration_url, data=sample_form_data)
        assert response.status_code == 302  # Should succeed

        # Now create enough registrations to reach the limit
        guardian = FosdemRegistrationGuardian.objects.create(
            name="Another Parent",
            email="parent2@example.com",
            contact_number="+32470111111",
        )

        for i in range(3):  # This brings us to 10 registrations
            FosdemRegistration.objects.create(
                session=submission,
                registering_person=guardian,
                nickname=f"Kid {i}",
                age=8,
            )

        # Now trying to register one more should fail
        over_limit_data = {
            "name": "Over Limit Parent",
            "email": "overlimit@example.com",
            "contact_number": "+32470999999",
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-nickname": "Over Limit Kid",
            "form-0-age": "9",
            "form-0-special_needs": "",
        }

        response = client.post(registration_url, data=over_limit_data)
        assert response.status_code == 200  # Should not redirect
        assert (
            "limit" in response.content.decode().lower()
            or "full" in response.content.decode().lower()
        )

    def test_registration_email_sending(
        self,
        client,
        registration_url,
        registration_track,
        submission,
        max_participants_answer,
        sample_form_data,
        mailoutbox,
    ):
        """Test that confirmation email is sent after registration."""
        response = client.post(registration_url, data=sample_form_data)
        assert response.status_code == 302

        # Check that email was sent
        assert len(mailoutbox) >= 1
        email = mailoutbox[0]
        assert "jane.doe@example.com" in email.to
        assert "registration" in email.subject.lower()


@pytest.mark.django_db
@pytest.mark.views
class TestViewPermissions:
    """Test view permissions and access control."""

    def test_anonymous_user_access(self, client, overview_url, detail_url):
        """Test that anonymous users cannot access protected views."""
        for url in [overview_url, detail_url]:
            response = client.get(url)
            assert response.status_code in [302, 403]

    def test_user_without_permission_access(
        self, client, user, overview_url, detail_url
    ):
        """Test that users without proper permissions cannot access views."""
        client.force_login(user)

        for url in [overview_url, detail_url]:
            response = client.get(url)
            assert response.status_code in [302, 403]

    def test_public_registration_form_access(self, client, registration_url):
        """Test that registration form is accessible to public."""
        response = client.get(registration_url)
        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.views
@pytest.mark.integration
class TestViewIntegration:
    """Integration tests for views working together."""

    def test_registration_workflow(
        self,
        client,
        authenticated_client,
        registration_url,
        overview_url,
        detail_url,
        registration_track,
        submission,
        max_participants_answer,
        sample_form_data,
    ):
        """Test complete registration workflow."""
        # 1. Check overview (no registrations initially)
        response = authenticated_client.get(overview_url)
        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 0

        # 2. Register children
        response = client.post(registration_url, data=sample_form_data)
        assert response.status_code == 302

        # 3. Check overview (should show 2 registrations)
        response = authenticated_client.get(overview_url)
        submissions = response.context["submissions"]
        submission_data = submissions.first()
        assert submission_data.nr_registrations == 2

        # 4. Check detail view
        response = authenticated_client.get(detail_url)
        registrations = response.context["object_list"]
        assert registrations.count() == 2
