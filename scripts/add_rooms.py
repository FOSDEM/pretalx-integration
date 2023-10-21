import csv
# \copy (select conference_room, size FROM conference_room where conference_id=16 order by rank) to ~/rooms.csv delimiter ',' CSV HEADER;

from pretalx.event.models import Event
from pretalx.schedule.models import Room

from django_scopes import scope, scopes_disabled

dest_slug='fosdem_2023'
dest = Event.objects.get(slug=dest_slug)

with scope(event=dest):
    with open('rooms.csv', newline='') as csvfile:
        reader=csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if dest.rooms.filter(name=row['name']).exists():
                continue
            room = Room(name=row['name'], capacity=row['capacity'], event=dest)
            room.save()
