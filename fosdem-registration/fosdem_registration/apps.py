from functools import lru_cache

import rules
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


@lru_cache(maxsize=128)
def user_can_access_registration(user_id, event_id):
    from pretalx.person.models import User

    from fosdem_registration.models import FosdemRegistrationTrack

    user = User.objects.get(id=user_id)
    teams = user.teams.all()
    if FosdemRegistrationTrack.objects.filter(teams__in=teams).exists():
        return True
    return False


@rules.predicate
def view_fosdem_registrations(user, event):
    if not event or not user.is_authenticated:
        return False
    return user_can_access_registration(user.id, event.id)


rules.add_perm("orga.view_fosdem_registrations", view_fosdem_registrations)
