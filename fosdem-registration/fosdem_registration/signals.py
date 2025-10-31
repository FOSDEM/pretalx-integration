from django.dispatch import receiver
from django.urls import reverse
from pretalx.orga.signals import nav_event_settings

# @receiver(nav_event_settings)
# def fosdem_registration_settings(sender, request, **kwargs):
#    if not request.user.has_perm("event.update_event", request.event):
#        return []
#    return [
#        {
#            "label": "FOSDEM registration",
#            "url": reverse(
#                "plugins:fosdem_registration:settings",
#                kwargs={"event": request.event.slug},
#            ),
#            "active": request.resolver_match.url_name
#            == "plugins:fosdem_registration:settings",
#        }
#    ]
#
