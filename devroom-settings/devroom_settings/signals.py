import logging

from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from pretalx.cfp.signals import html_below_track, on_save_track
from pretalx.common.signals import register_data_exporters
from pretalx.mail.placeholders import SimpleFunctionalMailTextPlaceholder
from pretalx.mail.signals import register_mail_placeholders
from pretalx.orga.signals import nav_event

from .forms import TrackSettingsForm
from .models import TrackSettings

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def track_email(event, track):
    """Get the track email if defined and return event mail otherwise"""
    try:
        mail = track.tracksettings.mail
    except:
        mail = event.email
    return mail


@receiver(register_mail_placeholders, dispatch_uid="devroom_settings_placeholders")
def devroom_placeholders(sender, **kwargs):
    """This allows setting the track mail address as reply-to address
    to confirmation mails sent by the system"""
    placeholders = [
        SimpleFunctionalMailTextPlaceholder(
            "track_mail",
            ["submission"],
            lambda submission: track_email(sender, submission.track),
            "toothbrush-devroom-managers@fosdem.org",
            "Email of the track responsible",
        ),
        SimpleFunctionalMailTextPlaceholder(
            "proposal_feedback_url",
            ["submission"],
            lambda submission: submission.urls.feedback,
            "https://pretalx.com/democon/me/submissions/F8VVL/feedback",
            "Url with talk feedback",
        ),
    ]
    return placeholders


@receiver(nav_event, dispatch_uid="devroom_report")
def navbar_info(sender, request, **kwargs):
    if not request.user.has_perm("event.orga_access_event", request.event):
        return []
    url = resolve(request.path_info)
    teams = request.user.teams.all()
    track_slugs = TrackSettings.objects.filter(
        manager_team__in=teams, track__event=request.event
    ).values_list("slug", flat=True)
    print(track_slugs)

    def make_devroom_link(slug, url_name, label):
        return {
            "label": label,
            "url": reverse(
                f"plugins:devroom_settings:{url_name}",
                kwargs={"event": request.event.slug, "track_slug": slug},
            ),
            "active": (
                url.namespace == "plugins:devroom_settings"
                and url.url_name == url_name
                and slug == request.resolver_match.kwargs.get("track_slug")
            ),
        }

    try:
        sublinks = [
            make_devroom_link(slug, "devroom-dashboard", f"{slug} settings")
            for slug in track_slugs
        ] + [
            make_devroom_link(slug, "devroom-team", f"{slug} team")
            for slug in track_slugs
        ]

        links = [
            {
                "label": "Devrooms",
                "icon": "user-plus",
                "active": True,
                "children": [
                    {
                        "label": "Overview",
                        "url": reverse(
                            "plugins:devroom_settings:devroom-report",
                            kwargs={
                                "event": request.event.slug,
                            },
                        ),
                        "active": url.namespace == "plugins:devroom_settings"
                        and url.url_name == "devroom-report",
                    },
                ],
            },
            {
                "label": "Feedback",
                "icon": "envelope",
                "url": reverse(
                    "plugins:devroom_settings:feedback_list",
                    kwargs={
                        "event": request.event.slug,
                    },
                ),
                "active": url.namespace == "plugins:devroom_settings"
                and url.url_name == "feedback_list",
            },
        ]
        links[0]["children"] += sublinks
    except Exception:
        logger.exception("navbar info")
    return links


# @receiver(register_data_exporters, dispatch_uid="nanoc_export")
# def register_data_exporter(sender, **kwargs):
#    from .nanoc import NanocExporter
#
#    return NanocExporter
