# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_scopes import scope, scopes_disabled
from django.utils.text import slugify

from pretalx.event.models import Event
from pretalx.submission.models import Track
from devroom_settings.models import TrackSettings, TrackManager

class Command(BaseCommand):
    help = 'Import accepted devrooms from another CfP as devrooms (track)'

    def add_arguments(self, parser):
        parser.add_argument("source", help="Source event slug")
        parser.add_argument("destination", help="Destination event slug")

    def handle(self, *args, **kwargs):
        source=kwargs["source"]
        source_event = Event.objects.get(slug=source)
        with scope(event=source_event):
            accepted_devrooms=source_event.submissions.filter(state__in =["confirmed", "accepted"]).order_by("title")

        dest=kwargs["destination"]
        dest_event = Event.objects.get(slug=dest)
        with scope(event=dest_event):
            existing_tracks=list(Track.objects.all().values_list('name', flat=True))

        for i, submission in enumerate(accepted_devrooms):
            if submission.title in existing_tracks:
                continue
            track = Track(name=submission.title, event=dest_event)
            track.color="#FFFFFF" # not used, but otherwise it will ask when you open the page
            track.position=i+len(existing_tracks)
            track.save()

            tracksetting= TrackSettings(track=track)
            tracksetting.track_type=TrackSettings.TrackType.DEVROOM

            tracksetting.slug=slugify(track.name)[0:63]
            print(f"adding {track.name}")
            tracksetting.save()
            for user in submission.speakers.all():
                track_manager = TrackManager(track=track, user=user).save()

