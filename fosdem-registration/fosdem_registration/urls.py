import logging

from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import RegisterPersonView, RegistrationOverview

logger = logging.getLogger(__name__)

logger.debug("loading fosdem_registration url")

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fosdem_registration/$",
        RegistrationOverview.as_view(),
        name="registration_overview",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/register/(?P<submission_code>[A-Z0-9]+)/$",
        RegisterPersonView.as_view(),
        name="register_person",
    ),
]
