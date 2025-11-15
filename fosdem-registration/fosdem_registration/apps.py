from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "fosdem_registration"
    verbose_name = "FOSDEM registration"

    class PretalxPluginMeta:
        name = gettext_lazy("FOSDEM registration")
        author = "Johan Van de Wauw"
        description = gettext_lazy("pretalx plugin for FOSDEM registration")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
        from . import urls
