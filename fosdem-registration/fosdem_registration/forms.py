from i18nfield.forms import I18nModelForm

from .models import FosdemRegistrationSettings


class FosdemRegistrationSettingsForm(I18nModelForm):
    def __init__(self, *args, event=None, **kwargs):
        self.instance, _ = FosdemRegistrationSettings.objects.get_or_create(event=event)
        super().__init__(*args, **kwargs, instance=self.instance, locales=event.locales)

    class Meta:
        model = FosdemRegistrationSettings
        fields = ("some_setting",)
        widgets = {}
