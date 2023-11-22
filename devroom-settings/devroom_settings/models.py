from django.db import models
from django_scopes import ScopedManager
from pretalx.event.models import Team
from pretalx.person.models import User
from pretalx.schedule.models import Room
from pretalx.submission.models import Track


class TrackSettings(models.Model):
    class TrackType(models.TextChoices):
        MAIN_TRACK = "MT", "main_track"
        LIGHTNING_TALK = "LT", "lightning_talk"
        DEVROOM = "D", "devroom"
        BOF_ROOM = "B", "bof"

    track = models.OneToOneField(to=Track, on_delete=models.CASCADE)
    track_type = models.CharField(choices=TrackType.choices)
    slug = models.SlugField(
        max_length=63, verbose_name="slug", help_text="SLUG used for URLS"
    )
    mail = models.EmailField(
        max_length=254,
        help_text="track responsible (must be fosdem list)",
        blank=True,
        default="",
    )
    cfp_url = models.CharField(
        max_length=254, help_text="URL added to the CfP page", blank=True, default=""
    )
    online_qa = models.BooleanField(
        "Online Q&A",
        help_text="Should an online Q&A be added for this track",
        default=False,
    )
    review_team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, related_name="review_track"
    )
    manager_team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, null=True, related_name="manager_track"
    )
    rooms = models.ManyToManyField(
        Room, help_text="Allowed rooms for track (not yet enforced)", blank=True
    )
