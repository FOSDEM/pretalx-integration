from devroom_settings.models import TrackSettings
from django.core.management.base import BaseCommand, CommandError
from django_scopes import scope
from pretalx.event.models import Event
from pretalx.event.models.organiser import Team
from pretalx.submission.models import Question

from fosdem_registration.models import FosdemRegistrationTrack


class Command(BaseCommand):
    help = "Activate track registration for a specific conference and track. Question must contain max number of participants."

    def add_arguments(self, parser):
        parser.add_argument("event_slug", type=str, help="The slug of the event")
        parser.add_argument("track_slug", type=str, help="The slug of the track")

    def handle(self, *args, **options):
        event_slug = options["event_slug"]
        track_slug = options["track_slug"]

        event = Event.objects.get(slug=event_slug)
        with scope(event=event):
            tracksettings = TrackSettings.objects.get(
                slug=track_slug, track__event=event
            )

            question = Question.objects.get(
                question__icontains="max number of participants", event=event
            )
            year = event.slug[-4:]
            teams = Team.objects.filter(name=f"managers-junior-{year}")
            if len(teams) == 0:
                print("no team found")
                exit(1)

            frt = FosdemRegistrationTrack.objects.create(
                track=tracksettings.track, max_number_question=question
            )
            frt.teams.set(teams)
