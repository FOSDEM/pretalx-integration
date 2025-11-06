from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import registration_overview

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fosdem_registration/$",
        registration_overview,
        name="fosdem_registration",
    ),
]
