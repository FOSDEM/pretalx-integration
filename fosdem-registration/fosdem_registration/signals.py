import logging

from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event

logger = logging.getLogger(__name__)

print("loading fosdem_registration signals")


@receiver(nav_event, dispatch_uid="fosdem_registration_toolbar")
def fosdem_registration_overview(sender, request, **kwargs):
    if not request.user.has_perm("event.orga_access_event", request.event):
        return []
    return [
        {
            "label": "Junior registration",
            "url": reverse(
                "plugins:fosdem_registration:registration_overview",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:fosdem_registration:registration_overview",
        }
    ]
