from django.db import models

from pretalx.submission.models import Track
from pretalx.event.models import Team

class TrackSettings(Track):
    slug = models.SlugField(max_length=63, verbose_name="slug", help_text="SLUG used for URLS")
    mail = models.EmailField(max_length=254, help_text="track responsible (must be fosdem list)")
    online_qa = models.BooleanField("Online Q&A")
    # review_team = models.ForeignKey(Team)
