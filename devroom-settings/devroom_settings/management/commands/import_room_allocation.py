import csv

from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event
from pretalx.schedule.models import Room
from pretalx.submission.models import Track

from devroom_settings.models import TrackRoom

event = Event.objects.get(slug="fosdem-2025")


def import_rooms(file_path):
    with open(file_path, "r") as csvfile, scope(event=event):
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Fetch related models
            track, _ = Track.objects.get_or_create(name=row["track"], event=event)
            room, _ = Room.objects.get_or_create(name=row["room"], event=event)

            TrackRoom.objects.create(
                track=track,
                room=room,
                saturday_morning=bool(row["sat_morning"]),
                saturday_afternoon=bool(row["sat_afternoon"]),
                sunday_morning=bool(row["sunday_morning"]),
                sunday_afternoon=bool(row["sunday_afternoon"]),
            )


import_rooms("./devrooms.csv")
