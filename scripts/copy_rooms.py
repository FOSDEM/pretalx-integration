# copies all rooms from one event to another
from copy import copy

from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event

source_slug = "fosdem-2024"
dest_slug = "fosdem-2025"

source = Event.objects.get(slug=source_slug)
dest = Event.objects.get(slug=dest_slug)

with scopes_disabled():
    source_rooms = source.rooms.all()

with scope(event=dest):
    for room in source_rooms:
        if dest.rooms.filter(name=room.name).exists():
            continue
        new_room = copy(room)
        new_room.pk = None
        new_room.event = dest
        new_room.save()
