import logging

from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import RegistrationOverview

logger = logging.getLogger(__name__)

logger.debug("loading fosdem_registration url")

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fosdem_registration/$",
        RegistrationOverview.as_view(),
        name="registration_overview",
    ),
]
