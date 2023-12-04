import sys
from datetime import datetime
import pytz

from django.core.management.base import BaseCommand
from pretalx.event.models import Event
from django_scopes import scope

class Command(BaseCommand):
    help = "Create a new schedule release"

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        with scope(event=event):
            warnings = event.wip_schedule.warnings
            if bool(warnings["talk_warnings"]):
                print("there are talk warnings")
                print(warnings["talk_warnings"])
                sys.exit(1)

            if event.wip_schedule.changes["count"] > 0:
                # Set the timezone to Europe/Brussels
                brussels_timezone = pytz.timezone('Europe/Brussels')

                # Get the current time in Brussels timezone
                current_time = datetime.now(brussels_timezone)

                # Format the current time to ISO 8601 with minute precision
                current_time = current_time.strftime('%Y-%m-%d %H:%M%z')
                event.wip_schedule.freeze(name=current_time)
            else:
                print("no changes - no release")
