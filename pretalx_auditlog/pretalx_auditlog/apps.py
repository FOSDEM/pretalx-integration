from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_auditlog"
    verbose_name = "Pretalx Postgres audit log"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx Postgres audit log")
        author = "Johan Van de Wauw"
        description = gettext_lazy("Log changes to pretalx models")
        visible = True
        version = "0.0.0"

    def ready(self):
        from . import models  # NOQA
        from . import signals  # NOQA
