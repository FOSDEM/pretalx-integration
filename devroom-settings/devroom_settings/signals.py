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


@receiver(html_below_track, dispatch_uid="devroom_settings")
def render_form_fragment(sender, track, **kwargs):
    try:
        settings = track.tracksettings
    except TrackSettings.DoesNotExist:
        settings = TrackSettings(track=track)
    except AttributeError:
        settings = TrackSettings()

    form = TrackSettingsForm(instance=settings)
    template = get_template("devroom_settings/form_fragment.html")
    html = template.render({"context": form})

    return html


@receiver(on_save_track, dispatch_uid="devroom_settings_save")
def check_and_save(sender, track, request, **kwargs):
    """Checks and saves extra track settings"""

    try:
        settings = track.tracksettings
    except TrackSettings.DoesNotExist:
        settings = TrackSettings(track=track)

    form = TrackSettingsForm(request.POST, track=track, instance=settings)
    if form.is_valid():
        form.save()


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
        )
    ]
    return placeholders


@receiver(nav_event, dispatch_uid="devroom_report")
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_perm("orga.view_orga_area", request.event):
        return []
    return [
        {
            "label": "Devrooms",
            "icon": "user-plus",
            "children": [
                {
                    "label": "Devroom-dashboard",
                    "url": reverse(
                        "plugins:devroom_settings:devroom-dashboard",
                        kwargs={"event": request.event.slug},
                    ),
                    "active": url.namespace == "plugins:devroom_settings"
                    and url.url_name == "devroom-dashboard",
                },
                {
                    "label": "Devroom-report",
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
        }
    ]


# @receiver(register_data_exporters, dispatch_uid="nanoc_export")
# def register_data_exporter(sender, **kwargs):
#    from .nanoc import NanocExporter
#
#    return NanocExporter
