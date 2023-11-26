from pathlib import Path
from shutil import copy2

from django.core.management.base import BaseCommand
from django_scopes import scope
from PIL import Image
from pretalx.event.models import Event

from pretalx_nanoc_exporter.nanoc import NanocExporter


class Command(BaseCommand):
    help = "Export to nanoc with resources/avatars"

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")
        parser.add_argument("destination_dir", help="Destination dir")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        dest_dir = Path(kwargs["destination_dir"])

        with scope(event=event):
            nanoc_exporter = NanocExporter(
                event=event, schedule=event.current_schedule, dest_dir=dest_dir
            )
            _, _, yaml_content = nanoc_exporter.render()

            with open(dest_dir / "pentabarf.yaml", "w") as f:
                f.write(yaml_content)
