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


RegistrationFormSet = modelformset_factory(
    FosdemRegistration,
    form=FosdemRegistrationForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
)
