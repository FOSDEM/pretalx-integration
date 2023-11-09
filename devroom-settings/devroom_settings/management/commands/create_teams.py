# craete teams for every devroom

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_scopes import scope, scopes_disabled
from django.utils.text import slugify

from pretalx.event.models import Event
from pretalx.submission.models import Track
from devroom_settings.models import TrackSettings, TrackManager

from pretalx.event.models import Organiser, Team

class Command(BaseCommand):
    help = 'Bulk create teams for devrooms'

    def add_arguments(self, parser):
        parser.add_argument("organiser", help="Organiser")
        parser.add_argument("event", help="Event slug")
    
    def handle(self, *args, **kwargs):
        event_slug=kwargs["event"]
        organiser_slug=kwargs["organiser"]
        event = Event.objects.get(slug=event_slug)
        organiser = Organiser.objects.get(slug=organiser_slug)


        with scope(event=event):
            tracks = Track.objects.filter(event=event, tracksettings__track_type='D').select_related("tracksettings")
        existing_teams=list(Team.objects.all().values_list('name', flat=True))
        for track in tracks:
            team_name=f"managers-{track.tracksettings.slug}-2024"
            if team_name in existing_teams:
                continue
            team = Team(name=team_name, organiser=organiser, can_change_submissions=True, is_reviewer=True)
            team.save()
            team.limit_events.set([event])
            team.save()
            track.tracksettings.manager_team=team
            track.tracksettings.save()
            with scope(event=event):
                trackmanagers=list(TrackManager.objects.filter(track=track).values_list('user', flat=True))
                print(trackmanagers)
            team.members.set(trackmanagers)
            team.save()

