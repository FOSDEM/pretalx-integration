from .models import TrackSettings,TrackManager
from pretalx.submission.models import Track
from django import forms

from django.forms import formset_factory
from django_scopes.forms import SafeModelChoiceField

class TrackSettingsForm(forms.ModelForm):

    #mail=forms.EmailField(disabled=True) # should not be changed
    def __init__(self, *args, track=None, **kwargs):
        self.track = track
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackSettings
        fields = ( "track_type", "slug", "mail", "online_qa", "cfp_url")


class TrackManagerForm(forms.ModelForm):
    def __init__(self, *args, event=None, **kwargs):
        self.event = event
        self.fields["track"].queryset=Track.objects.filter(event=event)
        super().__init__(*args, **kwargs)
    class Meta:
        model = TrackManager
        fields= ( "track", "user")
        field_classes = { 'track': SafeModelChoiceField}

DevroomFormSet = formset_factory(TrackManagerForm)

