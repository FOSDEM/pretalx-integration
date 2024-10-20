from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event


@receiver(nav_event, dispatch_uid="fringe_toolbar")
def pretalx_fringe_list(sender, request, **kwargs):
    if not request.user.has_perm("person.is_administrator", None):
        return []
    return [
        {
            "label": "Fringe",
            "icon": "meetup",
            "url": reverse(
                "plugins:pretalx_fringe:fringe_list",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name == "fringe_list",
        }
    ]
