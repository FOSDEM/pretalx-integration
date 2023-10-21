# copies all rooms from one event to another
from pretalx.event.models import Event

from django_scopes import scope, scopes_disabled

source_slug='fosdem_2023'
dest_slug='fosdem_2024'

source = Event.objects.get(slug=source_slug)
dest = Event.objects.get(slug=dest_slug)

with scopes_disabled():
  source_rooms = source.rooms.all()

with scope(event=dest):
  for room in source_rooms:
    if dest.rooms.filter(name=room.name).exists():
      continue
    new_room=copy(room)
    new_room.event=dest
    new_room.save()
