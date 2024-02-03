from pathlib import Path

import pytz
from django.core.management.base import BaseCommand
from django.db import models
from django_scopes import scope
from PIL import Image
from pretalx.event.models import Event
from pretalx.submission.models import SubmissionStates

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

        with scope(event=event):
            schedule = event.wip_schedule

            # Set visibility of talkslots
            filter = models.Q(
                models.Q(submission__state=SubmissionStates.CONFIRMED)
                | models.Q(submission__isnull=True),
                start__isnull=False,
                submission__on_website=True,
            )
            schedule.talks.all().update(is_visible=False)
            schedule.talks.filter(filter).update(is_visible=True)
            schedule.talks.exclude(filter).update(is_visible=False)

            nanoc_exporter = NanocExporter(
                event=event, schedule=schedule, dest_dir=dest_dir
            )
            _, _, yaml_content = nanoc_exporter.render()

            with open(dest_dir / "pentabarf.yaml", "w") as f:
                f.write(yaml_content)
