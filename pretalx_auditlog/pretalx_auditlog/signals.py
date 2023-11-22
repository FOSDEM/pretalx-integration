# Register your receivers here
from . import models  # NOQA
from django.dispatch import receiver
from pretalx.orga.signals import nav_global, nav_event
from django.urls import resolve, reverse


@receiver(nav_event, dispatch_uid="event_audit_log")
def navbar_info_event(sender, request, **kwargs):
    if not request.user.has_perm("person.is_administrator", None):
        return []
    return [
        {
            "label": "Audit-log",
            "icon": "wpforms",
            "url": reverse(
                "plugins:pretalx_auditlog:auditlog",
            ),
            "active": True,
        }
    ]

@receiver(nav_global, dispatch_uid="audit_log")
def navbar_info(sender, request, **kwargs):
    if not request.user.has_perm("person.is_administrator", None):
        return []
    return [
        {
            "label": "Audit-log",
            "icon": "wpforms",
            "url": reverse(
                "plugins:pretalx_auditlog:auditlog",
            ),
            "active": True,
        }
    ]