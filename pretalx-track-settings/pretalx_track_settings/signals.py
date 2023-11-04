from django.dispatch import receiver

from pretalx.cfp.signals import html_below_track, on_save_track
from .models import TrackSettings
from .forms import TrackSettingsForm

from django.template.loader import get_template

@receiver(html_below_track, dispatch_uid="pretalx_track_settings")
def render_form_fragment(sender, track, **kwargs):
    print("registering html below track")
    try:
        settings = track.tracksettings
    except TrackSettings.DoesNotExist:
        settings = TrackSettings(track_ptr=track)

    form = TrackSettingsForm(instance=settings)
    template = get_template("pretalx_track_settings/form_fragment.html")
    html = template.render({"context": form})

    return html


@receiver(on_save_track, dispatch_uid="pretalx_track_settings_save" )
def check_and_save(sender, event, request, **kwargs):
    print("hiep hoi")

    f = TrackSettingsForm(request.POST)
    f.event_id=event.pk
    print(f.event)
    # check (or in form) for duplicate slugs
    print(f)
    return f.save()
