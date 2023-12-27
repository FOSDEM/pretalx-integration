from django.views.generic import ListView, UpdateView

from django.urls import reverse
from pretalx.common.mixins.views import EventPermissionRequired
from pretalx.event.models import TeamInvite
from pretalx.submission.models import SubmitterAccessCode
from pretalx.event.forms import TeamInviteForm

from devroom_settings.forms import DevroomTrackSettingsForm, DevroomTrackForm, UserSettingsForm
from devroom_settings.models import TrackSettings, UserSettings


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
    context_object_name = "trackssettings"

    def get_queryset(self):
        teams = self.request.user.teams.all()
        tracksettings = (
            TrackSettings.objects.filter(
                manager_team__in=teams, track__event=self.request.event
            )
            .select_related("track")
            .select_related("review_team")
            .prefetch_related("review_team__members")
            .prefetch_related("manager_team")
            .prefetch_related("manager_team__members")
        ).order_by("track__position")
        return tracksettings

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = [
            DevroomTrackSettingsForm(prefix=track.slug, instance=track)
            for track in context["trackssettings"]
        ]
        devroom_forms = [
            DevroomTrackForm(prefix=f"ds_{track.slug}", instance=track.track)
            for track in context["trackssettings"]
        ]
        invite_forms = [
            TeamInviteForm(prefix=f"invite_{track.slug}") for track in context["trackssettings"]
        ]

        access_codes = [
            SubmitterAccessCode.objects.filter(track=track.track).values_list(
                "code", flat=True
            )
            for track in context["trackssettings"]
        ]

        context["track_forms"] = zip(
            context["trackssettings"], forms, invite_forms, devroom_forms, access_codes
        )

        return context

    def post(self, request, *args, **kwargs):
        tracksettings = self.get_queryset()
        for track in tracksettings:
            form = DevroomTrackSettingsForm(
                self.request.POST, prefix=track.slug, instance=track
            )
            if form.is_valid() and form.has_changed():
                form.save()

            form = DevroomTrackForm(
                self.request.POST, prefix=f"ds_{track.slug}", instance=track.track
            )
            if form.is_valid() and form.has_changed():
                form.save()

            invite_form = TeamInviteForm(self.request.POST, prefix=f"invite_{track.slug}")
            if invite_form.is_valid():
                invite = TeamInvite.objects.create(
                    team=track.review_team,
                    email=invite_form.cleaned_data["email"].lower().strip(),
                )
                invite.send()

        return self.get(request, *args, **kwargs)

class UserSettingsView(EventPermissionRequired, UpdateView):
    permission_required = "orga.change_submissions" # should only be login or sth
    template_name = "devroom_settings/user_fragment.html"
    model = UserSettings
    form_class=UserSettingsForm

    # fields = ("matrix_id",)
    def get_object(self):
        usersettings, created = UserSettings.objects.get_or_create(user=self.request.user)
        print(usersettings)
        return usersettings

    def get_success_url(self):
        return reverse("cfp:event.user.view", kwargs={"event": self.request.event.slug})
    # http://localhost:8000/democon/me/
