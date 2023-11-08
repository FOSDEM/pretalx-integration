from pretalx.common.mixins.views import EventPermissionRequired, PermissionRequired
from django.views.generic import TemplateView
from pretalx.event.models import Event
from pretalx.submission.models import Track
from devroom_settings.models import TrackSettings, TrackManager

from django.views.generic import ListView
from django_scopes import scope, scopes_disabled


class DevroomReport(EventPermissionRequired, ListView):
    permission_required = "orga.change_submissions"
    template_name = "devroom_settings/devroom-manager-report.html"
    context_object_name = "tracks"

    def get_queryset(self):
        tracks = (
            self.request.event.tracks.all()
            .select_related("tracksettings")
            .prefetch_related("trackmanager_set__user")
        )
        return tracks
