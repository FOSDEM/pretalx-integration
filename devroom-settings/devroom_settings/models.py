from django.db import models

from pretalx.submission.models import Track

from pretalx.person.models import User
from pretalx.event.models import Team
from pretalx.schedule.models import Room

from django_scopes import ScopedManager

class TrackSettings(models.Model):
    class TrackType(models.TextChoices):
        MAIN_TRACK="MT"
        LIGHTNING_TALK="LT"
        DEVROOM="D"
        BOF_ROOM="B"
    track = models.OneToOneField(to=Track, on_delete=models.CASCADE)
    track_type = models.CharField(choices=TrackType.choices)
    slug = models.SlugField(max_length=63, verbose_name="slug", help_text="SLUG used for URLS")
    mail = models.EmailField(max_length=254, help_text="track responsible (must be fosdem list)", blank=True, default="")
    cfp_url = models.CharField(max_length=254, help_text="URL added to the CfP page", blank=True, default="")
    online_qa = models.BooleanField("Online Q&A", help_text="Should an online QA be added for this ROOM", default=False)
    review_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    rooms = models.ManyToManyField(Room, help_text="Allowed rooms for track (not yet enforced)", blank=True)

class TrackManager(models.Model):
    track = models.ForeignKey(to=Track, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    objects = ScopedManager(event="track__event")