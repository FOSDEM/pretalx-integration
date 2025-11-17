from django import forms

from .models import FosdemRegistration


class FosdemRegistrationForm(forms.ModelForm):
    def __init__(self, *args, session=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def clean(self):
        # Attach session to instance for model clean
        if self.session:
            self.instance.session = self.session
        cleaned_data = super().clean()
        return cleaned_data

    class Meta:
        model = FosdemRegistration
        fields = ["nickname", "age"]
