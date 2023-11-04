from .models import TrackSettings
from pretalx.submission.models import Track
from django import forms



class TrackSettingsForm(forms.ModelForm):

    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackSettings
        fields = ("track_ptr", "slug", "mail", "online_qa")