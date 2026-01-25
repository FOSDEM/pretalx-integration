import logging

from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event

from fosdem_registration.models import FosdemRegistrationTrack

logger = logging.getLogger(__name__)


@receiver(nav_event, dispatch_uid="fosdem_registration_toolbar")
def fosdem_registration_overview(sender, request, **kwargs):
    logger.debug("checking permissions for fosdem registration")
    try:
        if not request.user.has_perm("orga.view_fosdem_registrations", request.event):
            return []
    except Exception as e:
        print(f"Error checking permissions for fosdem registration: {e}")
        return []

    return [
        {
            "label": "Junior registration",
            "icon": "child",
            "url": reverse(
                "plugins:fosdem_registration:registration_overview",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name == "registration_overview",
        }
    ]
