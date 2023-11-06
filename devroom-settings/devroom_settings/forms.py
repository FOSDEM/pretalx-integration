from .models import TrackSettings
from pretalx.submission.models import Track
from django import forms



class TrackSettingsForm(forms.ModelForm):

    #mail=forms.EmailField(disabled=True) # should not be changed
    def __init__(self, *args, track=None, **kwargs):
        self.track = track
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackSettings
        fields = ( "track_type", "slug", "mail", "online_qa", "cfp_url", "devroom_managers")


