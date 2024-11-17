from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import timedelta
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

    def clean(self):
        cleaned_data = super().clean()
        starts = cleaned_data.get("starts")
        ends = cleaned_data.get("ends")

        if starts and ends and ends < starts:
            raise ValidationError(
                {
                    "ends": "The end time must be greater than or equal to the start time."
                }
            )

        if starts < self.event.date_from - timedelta(days=30):
            raise ValidationError(
                {"starts": "Event starts more than 30 days before FOSDEM"}
            )
        if ends > self.event.date_to + timedelta(days=30):
            raise ValidationError({"ends": "Event ends more than 30 days after FOSDEM"})

        return cleaned_data

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
            "starts": forms.DateInput(format="%Y-%m-%d"),
            "ends": forms.DateInput(format="%Y-%m-%d"),
        }
