from django.db import models
from django.utils.text import slugify
from django_scopes import ScopedManager
from pretalx.event.models import Team
from pretalx.person.models import User
from pretalx.schedule.models import Room
from pretalx.submission.models import Submission, Track


class FosdemUser(models.Model):
    """Add extra info to users which are coupled to a talk

    For now used to add users which should be informed
    about talk changes but not be on the FOSDEM website
    """

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    hide_schedule = models.BooleanField(
        "Hide on schedule",
        help_text="Hide user from the published schedule",
        default=False,
    )

    class Meta:
        db_table = "fosdem_user"
