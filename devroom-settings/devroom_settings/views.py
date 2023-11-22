from django.views.generic import FormView, ListView, TemplateView
from django.views.generic.edit import FormMixin
from django_scopes import scope, scopes_disabled
from pretalx.common.mixins.views import EventPermissionRequired, PermissionRequired
from pretalx.event.models import Event
from pretalx.submission.models import Track

from devroom_settings.forms import DevroomForm
from devroom_settings.models import TrackSettings


class DevroomReport(EventPermissionRequired, ListView):
    permission_required = "orga.change_submissions"
    template_name = "devroom_settings/devroom-manager-report.html"
    context_object_name = "tracks"

    def get_queryset(self):
        tracks = (
            self.request.event.tracks.all()
            .select_related("tracksettings")
            .select_related("tracksettings__manager_team")
            .prefetch_related("tracksettings__manager_team__members")
            .prefetch_related("tracksettings__manager_team__invites")
        )
        return tracks


class DevroomDashboard(EventPermissionRequired, ListView):
    permission_required = "orga.change_submissions"
    template_name = "devroom_settings/devroom-dashboard.html"
    context_object_name = "tracks"

    def get_queryset(self):
        teams = self.request.user.teams.all()
        tracksettings = TrackSettings.objects.filter(
            manager_team__in=teams
        ).select_related("track")
        return tracksettings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = [
            DevroomForm(prefix=track.slug, instance=track)
            for track in context["tracks"]
        ]
        context["forms"] = forms
        context["tracks"] = zip(context["tracks"], forms)
        return context

    def post(self, request, *args, **kwargs):
        tracks = self.get_queryset()
        for track in tracks:
            form = DevroomForm(self.request.POST, prefix=track.slug, instance=track)
            if form.is_valid():
                form.save()
            else:
                print("form is invalid!")
        return self.get(request, *args, **kwargs)
