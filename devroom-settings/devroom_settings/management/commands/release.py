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
        parser.add_argument('-W', '--ignore_warnings', action='store_true', help='Ignore warnings and release anyway')
    

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        with scope(event=event):
            warnings = event.wip_schedule.warnings
            if bool(warnings["talk_warnings"]):
                print("there are talk warnings")
                print(warnings["talk_warnings"])
                if not kwargs["ignore_warnings"]:
                    sys.exit(1)
                else:
                    print("Ignoring warnings and releasing anyway")

            if event.wip_schedule.changes["count"] > 0:
                # Set the timezone to Europe/Brussels
                brussels_timezone = pytz.timezone('Europe/Brussels')
                # Get the current time in Brussels timezone
                current_time = datetime.now(brussels_timezone)
                # Format the current time to ISO 8601 with minute precision
                current_time = current_time.strftime('%Y-%m-%d %H:%M')
                event.wip_schedule.freeze(name=current_time, notify_speakers=True)
            else:
                print("no changes - no release")
