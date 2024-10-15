import csv

from django.core.management.base import BaseCommand
from django_scopes import scope
from pretalx.event.models import Event
from pretalx.schedule.models import Room

from devroom_settings.models import RoomSettings


class Command(BaseCommand):
    help = "Import room names and passwords from a CSV file into RoomSettings"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]

        with open(csv_file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                room_name = row["room_name"]
                password = row["password"]

                event = Event.objects.get(pk=4)
                with scope(event=event):
                    room = Room.objects.get(name__contains=room_name, event=event)

                room_settings, _ = RoomSettings.objects.get_or_create(room=room)
                room_settings.control_password = password
                room_settings.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully imported password for room: {room_name}"
                    )
                )
