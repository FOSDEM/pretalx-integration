# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event
from pretalx.submission.models import Track

from devroom_settings.models import TrackManager, TrackSettings


class Command(BaseCommand):
    help = "Export devroom mail aliases for "

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)

        # print all devroom managers (mail)

        # get tracks + tracksettings + devroom managers
        with scope(event=event):
            tracks = Track.objects.filter(event=event).select_related(
                "tracksettings"
            )  # not no .prefetch_related("trackmanager_set") because it gives issues with
            # this scopes thing

        print("devroom mail aliases")
        for track in tracks:
            try:
                with scopes_disabled():
                    managers = list(
                        track.trackmanager_set.all().values_list(
                            "user__email", flat=True
                        )
                    )
                print(
                    f"{track.tracksettings.mail}\t{','.join(managers)},devrooms@fosdem.org"
                )
            except TrackSettings.DoesNotExist:
                pass
        print("all devroom managers:")
        with scopes_disabled():
            for track in tracks:
                for manager in track.trackmanager_set.all():
                    print(manager.user.email)
