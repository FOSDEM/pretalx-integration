from datetime import datetime
from pathlib import Path
from shutil import copy2

import pytz
from django.core.management.base import BaseCommand
from django_scopes import scope
from PIL import Image
from pretalx.event.models import Event

from devroom_settings.nanoc import NanocExporter


class Command(BaseCommand):
    help = "Export to nanoc with resources/avatars"

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")
        parser.add_argument("destination_dir", help="Destination dir")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        dest_dir = Path(kwargs["destination_dir"])

        # create a release
        if event.wip_schedule.changes["count"] > 0:
            # Set the timezone to Europe/Brussels
            brussels_timezone = pytz.timezone("Europe/Brussels")
            # Get the current time in Brussels timezone
            current_time = datetime.now(brussels_timezone)
            # Format the current time to ISO 8601 with minute precision
            current_time = current_time.strftime("%Y-%m-%d %H:%M")
            event.wip_schedule.freeze(name=current_time, notify_speakers=False)

        with scope(event=event):
            schedule = event.current_schedule
            nanoc_exporter = NanocExporter(
                event=event, schedule=schedule, dest_dir=dest_dir
            )
            _, _, yaml_content = nanoc_exporter.render()

            with open(dest_dir / "pentabarf.yaml", "w") as f:
                f.write(yaml_content)
