from django.dispatch import receiver

from pretalx.cfp.signals import html_below_track, on_save_track
from .models import TrackSettings
from .forms import TrackSettingsForm

from django.template.loader import get_template

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


@receiver(on_save_track, dispatch_uid="devroom_settings_save" )
def check_and_save(sender, track, request, **kwargs):
    """Checks and saves extra track settings"""
    f = TrackSettingsForm(request.POST, track=track)

    # There is most certainly a more Django way of doing this
    # take the value from the form and add the track by hand
    settings= f.save(commit=False)
    # check for existing ids
    try:
        settings.id = track.tracksettings.pk
    except TrackSettings.DoesNotExist:
        pass
    settings.track=track
    settings.save()
    f.save_m2m()
