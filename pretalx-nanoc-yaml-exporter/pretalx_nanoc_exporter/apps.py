from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

print("*** loading nanoc app")

class PluginApp(AppConfig):
    name = "pretalx_nanoc_exporter"
    verbose_name = "Pretalx exporter for nanoc (FOSDEM)"

    class PretalxPluginMeta:
        name = _("Pretalx exporter for nanoc (FOSDEM)")
        author = "Johan Van de Wauw"
        description = _("Plugin that generates yaml used for building the fosdem website")
        visible = True
        version = "0.0.0"
        restricted = False
        version="0.0.1"

    def ready(self):
        from . import signals  # noqa
