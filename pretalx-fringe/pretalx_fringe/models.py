from django.db import models
from pretalx.person.models.user import User


class FringeActivity(models.Model):
    event = models.ForeignKey(
        to="event.Event",
        on_delete=models.CASCADE,
        related_name="fringe_activities",
    )
    name = models.CharField(
        max_length=255, blank=False, null=False, help_text="Name of the Event"
    )
    url = models.URLField(
        help_text="Event website URL"
    )  # Using URLField for validation
    location = models.CharField(
        max_length=255, blank=False, null=False, help_text="Location of the event"
    )
    description = models.TextField(help_text="Description of the event")
    why = models.TextField(
        help_text="Why should it be listed as part of FOSDEM Fringe?"
    )
    starts = models.DateField(help_text="Start date (format %Y-%M-%d)")
    ends = models.DateField(help_text="End date (format %Y-%M-%d)")
    cost = models.CharField(max_length=255, blank=True, null=True)
    registration = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Any registration restrictions (e.g. By a specified date, By invitation only, None etc.)",
    )
    contact = models.EmailField(help_text="Public contact email")
    online = models.BooleanField(
        default=False, help_text="Publish to the FOSDEM website"
    )
    submitter = models.ForeignKey(to=User, on_delete=models.CASCADE)
    sort_order = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set sort_order to id * 10 if not defined
        if self.sort_order is None:
            if self.id is None:
                super().save(*args, **kwargs)
            self.sort_order = self.id * 10
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["sort_order"]
