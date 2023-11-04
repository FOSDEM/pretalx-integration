from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_track_settings"
    verbose_name = "Pretalx extra track settings"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx extra track settings")
        author = "Johan Van de Wauw"
        description = gettext_lazy("Store extra info per track")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
