from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_suggest"
    verbose_name = "pretalx suggest plugin"

    class PretalxPluginMeta:
        name = gettext_lazy("pretalx suggest plugin")
        author = "Johan Van de Wauw"
        description = gettext_lazy("Submit suggest events on pretalx")
        visible = True
        version = __version__
        category = "FEATURE"

    def ready(self):
        from . import signals  # noqa
        from . import urls


default_app_config = "pretalx_suggest.PluginApp"

import rules


@rules.predicate
def is_fosdem_staff(user, obj):
    groups = [str(t.name).lower() for t in user.teams.all()]
    return "fosdem staff team" in groups


rules.add_perm("orga.suggest_edit", is_fosdem_staff)
