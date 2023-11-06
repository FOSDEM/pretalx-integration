# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_scopes import scope, scopes_disabled
from django.utils.text import slugify

from pretalx.event.models import Event
from pretalx.submission.models import Track
from devroom_settings.models import TrackSettings

class Command(BaseCommand):
    help = 'Import accepted devrooms from another CfP as devrooms (track)'

    def add_arguments(self, parser):
        parser.add_argument("source", help="Source event slug")
        parser.add_argument("destination", help="Destination event slug")

    def handle(self, *args, **kwargs):
        source=kwargs["source"]
        source_event = Event.objects.get(slug=source)
        with scope(event=source_event):
            accepted_devrooms=source_event.submissions.filter(state__in =["confirmed", "accepted"])
        print(accepted_devrooms)

        dest=kwargs["destination"]
        dest_event = Event.objects.get(slug=dest)


        for submission in accepted_devrooms:
            track = Track(name=submission.title, event=dest_event)
            track.color="#FFFFFF" # not used, but otherwise it will ask when you open the page
            tracksetting= TrackSettings(track=track)

            tracksetting.slug=slugify(track.name)

            track.save()
            tracksetting.save()
            tracksetting.devroom_managers.set(submission.speakers.all())
            tracksetting.save()

