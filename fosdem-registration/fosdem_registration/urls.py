import logging

from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import (
    GuardianWithRegistrationsCreateView,
    RegistrationDetail,
    RegistrationOverview,
)

logger = logging.getLogger(__name__)

logger.debug("=" * 80)
logger.debug("FOSDEM REGISTRATION URLs MODULE LOADING")
logger.debug(f"Module name: {__name__}")
logger.debug("=" * 80)

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fosdem_registration/$",
        RegistrationOverview.as_view(),
        name="registration_overview",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fosdem_registration/(?P<submission_code>[A-Z0-9]+)/$",
        RegistrationDetail.as_view(),
        name="registration_detail",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/register/(?P<submission_code>[A-Z0-9]+)/$",
        GuardianWithRegistrationsCreateView.as_view(),
        name="register_person",
    ),
]

logger.debug(f"URL patterns defined: {len(urlpatterns)}")
for pattern in urlpatterns:
    logger.debug(f"  - {pattern.pattern} -> {pattern.name}")
