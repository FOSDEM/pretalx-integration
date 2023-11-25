from pretalx.event.models import Event
from pretalx.schedule.models import Room, Availability

from django_scopes import scope, scopes_disabled

event_slug='fosdem-2024'
event = Event.objects.get(slug=event_slug)

with scope(event=event):
    for room in event.rooms.all():
        if room.availabilities.count()>0:
            continue
        sat = Availability(room=room, event=event, start='2024-02-04T08:00:00+00:00', end='2024-02-04T16:00:00+00:00')
        sat.save()
        sun = Availability(room=room, event=event, start='2024-02-03T09:30:00+00:00', end='2024-02-03T18:00:00+00:00')
        sun.save()