from i18nfield.forms import I18nModelForm

from .models import NanocExportSettings


class NanocExportSettingsForm(I18nModelForm):
    def __init__(self, *args, event=None, **kwargs):
        self.instance, _ = NanocExportSettings.objects.get_or_create(event=event)
        super().__init__(*args, **kwargs, instance=self.instance, locales=event.locales)

    class Meta:
        model = NanocExportSettings
        fields = ("some_setting",)
        widgets = {}
