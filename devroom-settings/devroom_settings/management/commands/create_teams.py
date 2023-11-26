# craete teams for every devroom

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event, Organiser, Team
from pretalx.submission.models import Track



class Command(BaseCommand):
    help = "Bulk create review teams for devrooms"

    def add_arguments(self, parser):
        parser.add_argument("organiser", help="Organiser")
        parser.add_argument("event", help="Event slug")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        organiser_slug = kwargs["organiser"]
        event = Event.objects.get(slug=event_slug)
        organiser = Organiser.objects.get(slug=organiser_slug)

        with scope(event=event):
            tracks = Track.objects.filter(
                event=event, tracksettings__track_type="D"
            ).select_related("tracksettings")
        existing_teams = list(Team.objects.all().values_list("name", flat=True))
        for track in tracks:
            team_name = f"reviewers-{track.tracksettings.slug}-2024"
            if team_name in existing_teams:
                continue
            team = Team(
                name=team_name,
                organiser=organiser,
                can_change_submissions=False,
                is_reviewer=True,

            )
            team.save()
            team.limit_events.set([event])
            with scope(event=event):
                team.limit_tracks.set([track])
            team.save()
            track.tracksettings.review_team = team
            track.tracksettings.save()
