from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event

print("***** reading suggest signals")


@receiver(nav_event, dispatch_uid="suggest_toolbar")
def pretalx_suggest_list(sender, request, **kwargs):
    if not request.user.has_perm("orga.suggest_edit", request.event):
        return []

    return [
        {
            "label": "suggest",
            "icon": "meetup",
            "url": reverse(
                "plugins:pretalx_suggest:suggest_list",
                kwargs={"event": request.event.slug},
            ),
            "active": request.resolver_match.url_name == "suggest_list",
        }
    ]
