from django import forms
from pretalx.common.mixins.forms import I18nHelpText, ReadOnlyFlag
from pretalx.event.models import TeamInvite
from pretalx.submission.models import Track
from .models import TrackSettings, UserSettings


class TrackSettingsForm(forms.ModelForm):
    # mail=forms.EmailField(disabled=True) # should not be changed, but disabling causes issues
    def __init__(self, *args, track=None, **kwargs):
        self.track = track
        super().__init__(*args, **kwargs)

    def form_valid(self):
        self.instance.track = self.track
        super().form_valid()

    class Meta:
        model = TrackSettings
        fields = (
            "track_type",
            "slug",
            "mail",
            "online_qa",
            "cfp_url",
            "manager_team",
            "review_team",
        )


class DevroomTrackSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = TrackSettings
        fields = ("online_qa", "cfp_url")


class DevroomTrackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Track
        fields = ("requires_access_code",)


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ("matrix_id",)