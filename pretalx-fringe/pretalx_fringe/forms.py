from django import forms
from pretalx.common.mixins.forms import I18nHelpText, ReadOnlyFlag

from .models import FringeActivity


class FringeActivityForm(forms.ModelForm):
    def __init__(self, *args, event=None, user=None, admin=False, **kwargs):
        self.event = event
        self.user = user
        self.admin = admin
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.event:
            instance.event = self.event
        if self.user:
            instance.submitter = self.user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = FringeActivity
        fields = [
            "name",
            "location",
            "description",
            "why",
            "url",
            "starts",
            "ends",
            "cost",
            "registration",
            "contact",
            "online",
        ]
        widgets = {
            "starts": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
