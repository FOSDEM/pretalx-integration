from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event_settings


@receiver(nav_event_settings)
def pretalx_nanoc_export_settings(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        return []
    return [
        {
            "label": "nanoc-export",
            "url": reverse(
                "plugins:pretalx_nanoc_export:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_nanoc_export:settings",
        }
    ]
