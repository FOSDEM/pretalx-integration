from django import forms
from django.forms import modelformset_factory

from .models import FosdemRegistration, FosdemRegistrationGuardian


class FosdemRegistrationForm(forms.ModelForm):
    class Meta:
        model = FosdemRegistration
        fields = ["nickname", "age", "special_needs"]


class FosdemRegistrationGuardianForm(forms.ModelForm):
    class Meta:
        model = FosdemRegistrationGuardian
        fields = ["name", "email", "contact_number"]


class RemoveRegistrationForm(forms.Form):
    removal_reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        required=False,
        label="Reason for removal (optional)",
        help_text="Optionally provide a reason for removing this registration",
    )


RegistrationFormSet = modelformset_factory(
    FosdemRegistration,
    form=FosdemRegistrationForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
)
