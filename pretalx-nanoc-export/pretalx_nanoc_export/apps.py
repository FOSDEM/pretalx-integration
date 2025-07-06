from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_nanoc_export"
    verbose_name = "nanoc-export"

    class PretalxPluginMeta:
        name = gettext_lazy("nanoc-export")
        author = "Johan Van de Wauw"
        description = gettext_lazy("pretalx plugin for nanoc-export")
        visible = True
        version = __version__
        category = "EXPORTER"

    def ready(self):
        from . import signals  # NOQA
