from shutil import copy2
from pathlib import Path

from django.core.management.base import BaseCommand
from django_scopes import scope

from pretalx.event.models import Event


class Command(BaseCommand):
    help = 'Export submission resources'

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")
        parser.add_argument("destination_dir", help="Destination dir")

    def handle(self, *args, **kwargs):
        event_slug=kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        dest_dir = Path(kwargs["destination_dir"])
        for item in dest_dir.glob('*'):
            if item.is_file():
                item.unlink()
        dest_dir.rmdir()
        dest_dir.mkdir(parents=True, exist_ok=True)

        with scope(event=event):
            for talk in event.talks:
                for resource in talk.active_resources:
                    if resource.resource:
                        print(f"{resource.url} => {resource.resource.path}")
                        copy2(resource.resource.path, dest_dir)
            for speaker in event.speakers:
                if speaker.avatar:
                    print(f"{speaker.avatar.url} => {speaker.avatar.path}")
                    copy2(speaker.avatar.path, dest_dir)
