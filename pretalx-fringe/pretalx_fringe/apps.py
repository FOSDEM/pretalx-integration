from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_fringe"
    verbose_name = "pretalx fringe plugin"

    class PretalxPluginMeta:
        name = gettext_lazy("pretalx fringe plugin")
        author = "Johan Van de Wauw"
        description = gettext_lazy("Submit fringe events on pretalx")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # NOQA
