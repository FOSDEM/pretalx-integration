from django.dispatch import receiver

from pretalx.cfp.signals import html_below_track, on_save_track
from pretalx.mail.signals import register_mail_placeholders

from pretalx.orga.signals import nav_event
from pretalx.mail.placeholders import SimpleFunctionalMailTextPlaceholder
from .models import TrackSettings
from .forms import TrackSettingsForm

from django.template.loader import get_template
from django.urls import resolve, reverse


@receiver(html_below_track, dispatch_uid="devroom_settings")
def render_form_fragment(sender, track, **kwargs):
    print("registering html below track")
    try:
        settings = track.tracksettings
    except TrackSettings.DoesNotExist:
        settings = TrackSettings(track=track)

    form = TrackSettingsForm(instance=settings)
    template = get_template("devroom_settings/form_fragment.html")
    html = template.render({"context": form})

    return html


@receiver(on_save_track, dispatch_uid="devroom_settings_save")
def check_and_save(sender, track, request, **kwargs):
    """Checks and saves extra track settings"""
    f = TrackSettingsForm(request.POST, track=track)

    # There is most certainly a more Django way of doing this
    # take the value from the form and add the track by hand
    settings = f.save(commit=False)
    # check for existing ids
    try:
        settings.id = track.tracksettings.pk
    except TrackSettings.DoesNotExist:
        pass
    settings.track = track
    settings.save()


def track_email(track):
    """Get the track email if defined and return event mail otherwise"""
    try:
        mail = track.tracksettings.mail
    except TrackSettings.DoesNotExist:
        mail = track.event.email
    return mail


@receiver(register_mail_placeholders, dispatch_uid="devroom_settings_placeholders")
def devroom_placeholders(sender, **kwargs):
    """This allows setting the track mail address as reply-to address
    to confirmation mails sent by the system"""
    placeholders = [
        SimpleFunctionalMailTextPlaceholder(
            "track_mail",
            ["submission"],
            lambda submission: track_email(submission.track),
            "toothbrush-devroom-managers@fosdem.org",
            "Email of the track responsible",
        )
    ]
    return placeholders


@receiver(nav_event, dispatch_uid="devroom_report")
def navbar_info(sender, request, **kwargs):
    print("************parsing navbar info")
    url = resolve(request.path_info)
    if not request.user.has_perm("orga.view_orga_area", request.event):
        print("*** insufficient permissions navbar")
        return []
    return [
        {
            "label": "Devrooms",
            "icon": "user-plus",
            "url": reverse(
                "plugins:devroom_settings:devroom-report",
                kwargs={
                    "event": request.event.slug,
                },
            ),
            "active": True,
        }
    ]
