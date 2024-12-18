from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "devroom_settings"
    verbose_name = "Pretalx devroom settings"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx extra track settings")
        author = "Johan Van de Wauw"
        description = gettext_lazy("Store extra info per track")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
        from . import urls  # NOQA
