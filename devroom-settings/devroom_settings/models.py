from django.db import models
from django.utils.text import slugify
from django_scopes import ScopedManager
from pretalx.event.models import Team
from pretalx.person.models import User
from pretalx.schedule.models import Room
from pretalx.submission.models import Submission, Track


class TrackSettings(models.Model):
    class TrackType(models.TextChoices):
        MAIN_TRACK = "MT", "maintrack"
        KEYNOTE = "K", "keynote"
        LIGHTNING_TALK = "LT", "lightningtalk"
        DEVROOM = "D", "devroom"
        BOF_ROOM = "B", "bof"
        JUNIOR = "J", "junior"
        CERTIFICATION = "C", "certification"
        OTHER = "O", "other"

    track = models.OneToOneField(to=Track, on_delete=models.CASCADE)
    track_type = models.CharField(choices=TrackType.choices, max_length=50)
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

    def save(self, *args, **kwargs):
        if self.pk:
            self.slug = slugify(self.slug)
            old_instance = TrackSettings.objects.get(pk=self.pk)
            event = old_instance.track.event
            year = str(event.name)[-4:]
            if old_instance.slug != self.slug:
                # Trigger action when the slug changes
                if self.review_team:
                    self.review_team.name = f"review-{self.slug}-{year}"
                    self.review_team.save()
                if self.manager_team:
                    self.manager_team.name = f"manager-{self.slug}-{year}"
                    self.manager_team.save()
                # mail should be stable from now on
                # self.mail = f"{self.slug}-devroom-manager@fosdem.org"
        if self.cfp_url and self.cfp_url != "":
            self.track.description = (
                f"Make sure you read the track CfP details at {self.cfp_url}"
            )
            self.track.save()

        super().save(*args, **kwargs)


class TrackRoom(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    saturday_morning = models.BooleanField(default=False)
    saturday_afternoon = models.BooleanField(default=False)
    sunday_morning = models.BooleanField(default=False)
    sunday_afternoon = models.BooleanField(default=False)


class RoomSettings(models.Model):
    room = models.OneToOneField(to=Room, on_delete=models.CASCADE)
    visible = models.BooleanField(
        "Room Visible",
        help_text="Should content of this room be exported to the website",
        default=True,
    )
    control_password = models.CharField(
        "Password Video control", blank=True, null=True, max_length=64
    )


feedback_choices = [
    (5, "Very Good"),
    (4, "Good"),
    (3, "Neutral"),
    (2, "Bad"),
    (1, "Very Bad"),
]
important_choices = [
    (5, "Very Important"),
    (4, "Important"),
    (3, "Neutral"),
    (2, "Not Important"),
    (1, "Irrelevant"),
]


class FosdemFeedback(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    personal_knowledge = models.IntegerField(
        null=True,
        blank=True,
        help_text="How would you rate your personal knowledge about this topic?",
        choices=feedback_choices,
    )
    content_importance = models.IntegerField(
        null=True,
        blank=True,
        help_text="How important is this topic for this conference?",
        choices=important_choices,
    )
    content_quality = models.IntegerField(
        null=True,
        blank=True,
        help_text="What is your impression of the quality of the content?",
        choices=feedback_choices,
    )
    presentation_quality = models.IntegerField(
        null=True,
        blank=True,
        help_text="What is your impression of the presentation?",
        choices=feedback_choices,
    )
    feedback = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fosdem_feedback"
