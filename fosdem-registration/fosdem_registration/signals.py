import logging

from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event_settings

logger = logging.getLogger(__name__)

print("loading fosdem_registration signals")


@receiver(nav_event_settings)
def fosdem_registration_overview(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        print("xxxx")
        return []
    return [
        {
            "label": "FOSDEM registration",
            "url": reverse(
                "plugins:fosdem_registration:registration_overview",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:fosdem_registration:registration_overview",
        }
    ]
