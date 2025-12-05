from copy import copy

from django.core.management.base import BaseCommand, CommandError
from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event


class Command(BaseCommand):
    help = "Copy all rooms from one event to another."

    def add_arguments(self, parser):
        parser.add_argument("source_slug", help="Slug of the source event")
        parser.add_argument("dest_slug", help="Slug of the destination event")

    def handle(self, *args, **options):
        source_slug = options["source_slug"]
        dest_slug = options["dest_slug"]

        try:
            source = Event.objects.get(slug=source_slug)
        except Event.DoesNotExist:
            raise CommandError(f"Source event '{source_slug}' does not exist.")

        try:
            dest = Event.objects.get(slug=dest_slug)
        except Event.DoesNotExist:
            raise CommandError(f"Destination event '{dest_slug}' does not exist.")

        self.stdout.write(
            self.style.SUCCESS(f"Copying rooms from '{source_slug}' → '{dest_slug}'")
        )

        with scopes_disabled():
            source_rooms = list(source.rooms.all())

        with scope(event=dest):
            for room in source_rooms:
                if dest.rooms.filter(name=room.name).exists():
                    self.stdout.write(f" - Skipping existing room: {room.name}")
                    continue

                new_room = copy(room)
                new_room.pk = None
                new_room.guid = None
                new_room.event = dest
                new_room.save()

                self.stdout.write(
                    self.style.SUCCESS(f" - Created room: {new_room.name}")
                )

        self.stdout.write(self.style.SUCCESS("Done."))
