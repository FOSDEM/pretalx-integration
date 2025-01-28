from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import timedelta
from pretalx.common.forms.mixins import I18nHelpText, ReadOnlyFlag

from .models import TalkSuggestion


class TalkSuggestionForm(forms.ModelForm):
    def __init__(self, *args, user=None, admin=False, **kwargs):
        self.user = user
        self.admin = admin

        super().__init__(*args, **kwargs)
        if self.admin:
            self.fields["internal_notes"].required = True
        else:
            self.fields["internal_notes"].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.submitter = self.user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = TalkSuggestion
        fields = [
            "name",
            "why",
            "speaker_connection",
            "contact",
            "other",
            "internal_notes",
        ]
