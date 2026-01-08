#!/usr/bin/env python
"""
Data export script for fosdem_registration tests.
Run this script from your Django shell to export real data for testing:

    python manage.py shell < export_test_data.py

This will create JSON fixtures that can be used in your tests.
"""
import json
import os

from django.contrib.auth.models import Permission, User
from django.core import serializers
from django_scopes import scopes_disabled
from pretalx.event.models import Event, Team
from pretalx.person.models import SpeakerProfile, User as PretalxUser
from pretalx.submission.models import (
    Answer,
    Question,
    Submission,
    SubmissionType,
    Track,
)

from fosdem_registration.models import (
    FosdemRegistration,
    FosdemRegistrationGuardian,
    FosdemRegistrationTrack,
)


def export_test_data():
    """Export data from your running Django instance for tests."""

    # Create fixtures directory
    fixtures_dir = "tests/fixtures"
    os.makedirs(fixtures_dir, exist_ok=True)

    # Get a sample event (adjust slug as needed)
    try:
        # Try to get a FOSDEM event or any available event
        print(Event.objects.all())
        event = Event.objects.filter(slug="fosdem-2026").first()
        if not event:
            event = Event.objects.first()

        if not event:
            print("No events found. Please create an event first.")
            return

        print(f"Using event: {event.slug}")

        # Export event data
        event_data = serializers.serialize("json", [event])
        with open(f"{fixtures_dir}/event.json", "w") as f:
            f.write(event_data)

        # Export tracks with registration requirements
        reg_tracks = FosdemRegistrationTrack.objects.filter(
            track__event=event
        ).select_related("track", "max_number_question")

        tracks_to_export = [rt.track for rt in reg_tracks]
        questions_to_export = [rt.max_number_question for rt in reg_tracks]

        if tracks_to_export:
            tracks_data = serializers.serialize("json", tracks_to_export)
            with open(f"{fixtures_dir}/tracks.json", "w") as f:
                f.write(tracks_data)

            questions_data = serializers.serialize("json", questions_to_export)
            with open(f"{fixtures_dir}/questions.json", "w") as f:
                f.write(questions_data)

            reg_tracks_data = serializers.serialize("json", reg_tracks)
            with open(f"{fixtures_dir}/registration_tracks.json", "w") as f:
                f.write(reg_tracks_data)

        # Export submissions for these tracks
        submissions = Submission.objects.filter(
            track__in=tracks_to_export, event=event
        )[
            :5
        ]  # Limit to 5 for testing

        if submissions:
            submissions_data = serializers.serialize("json", submissions)
            with open(f"{fixtures_dir}/submissions.json", "w") as f:
                f.write(submissions_data)

        # Export submission types
        submission_types = SubmissionType.objects.filter(event=event)
        if submission_types:
            types_data = serializers.serialize("json", submission_types)
            with open(f"{fixtures_dir}/submission_types.json", "w") as f:
                f.write(types_data)

        # Export answers for max_number questions
        answers = Answer.objects.filter(
            submission__in=submissions, question__in=questions_to_export
        )

        if answers:
            answers_data = serializers.serialize("json", answers)
            with open(f"{fixtures_dir}/answers.json", "w") as f:
                f.write(answers_data)

        # Export registrations (anonymized)
        registrations = FosdemRegistration.objects.filter(
            session__in=submissions
        ).select_related("registering_person")[
            :10
        ]  # Limit to 10

        guardians = [reg.registering_person for reg in registrations]

        if guardians:
            # Anonymize guardian data for tests
            for guardian in guardians:
                guardian.name = f"Test Guardian {guardian.id}"
                guardian.email = f"guardian{guardian.id}@test.example.com"
                guardian.contact_number = f"+32470{guardian.id:06d}"

            guardians_data = serializers.serialize("json", guardians)
            with open(f"{fixtures_dir}/guardians.json", "w") as f:
                f.write(guardians_data)

        if registrations:
            # Anonymize registration data
            for reg in registrations:
                reg.nickname = f"Test Child {reg.id}"
                reg.special_needs = (
                    "No special needs" if not reg.special_needs else reg.special_needs
                )

            registrations_data = serializers.serialize("json", registrations)
            with open(f"{fixtures_dir}/registrations.json", "w") as f:
                f.write(registrations_data)

        # Export teams with access
        teams = Team.objects.filter(
            fosdemregistrationtrack__track__event=event
        ).distinct()

        if teams:
            teams_data = serializers.serialize("json", teams)
            with open(f"{fixtures_dir}/teams.json", "w") as f:
                f.write(teams_data)

        # Export users (create test users based on existing ones)
        users = PretalxUser.objects.filter(teams__in=teams).distinct()[
            :3
        ]  # Limit to 3 users

        if users:
            # Anonymize user data
            for user in users:
                user.email = f"testuser{user.id}@example.com"
                user.name = f"Test User {user.id}"
                user.nick = f"testuser{user.id}"

            users_data = serializers.serialize("json", users)
            with open(f"{fixtures_dir}/users.json", "w") as f:
                f.write(users_data)

        # Create a summary file
        summary = {
            "exported_at": str(timezone.now()),
            "event_slug": event.slug,
            "event_name": str(event.name),
            "counts": {
                "tracks": len(tracks_to_export),
                "submissions": submissions.count(),
                "registrations": registrations.count(),
                "guardians": len(guardians) if guardians else 0,
                "teams": teams.count() if teams else 0,
                "users": users.count() if users else 0,
            },
        }

        with open(f"{fixtures_dir}/export_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"Successfully exported test data to {fixtures_dir}/")
        print(f"Summary: {json.dumps(summary['counts'], indent=2)}")

    except Exception as e:
        print(f"Error during export: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    from django.utils import timezone

    with scopes_disabled():
        export_test_data()
