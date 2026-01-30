from django.core.management.base import BaseCommand
from django.db.models import Q
from django_scopes import scope
from pretalx.event.models import Event
from pretalx.schedule.models import Room

from devroom_settings.models import RoomSettings


class Command(BaseCommand):
    help = "Import room names and passwords from a CSV file into RoomSettings"

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]
        event_slug = options["event"]
        event = Event.objects.get(slug=event_slug)

        with open(csv_file_path, "r") as file:
            for line in file:
                day_room, password = line.split(":")
                try:
                    day, room_slug = day_room.split("-")
                except ValueError:
                    print(f"skipping {day_room}, not a day-devroom combination")
                    continue

                with scope(event=event):
                    room = (
                        Room.objects.filter(event=event)
                        .filter(Q(name=room_slug) | Q(name__icontains=room_slug))
                        .first()
                    )

                if room is None:
                    print(f"skipping {room_slug}, not known in pretalx")
                    continue
                room_settings, _ = RoomSettings.objects.get_or_create(room=room)
                if day == "1":
                    room_settings.control_password_day1 = password
                elif day == "2":
                    room_settings.control_password_day2 = password
                else:
                    raise ValueError("invalid day")

                room_settings.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully imported password for room: {room}"
                    )
                )
