from django.http import JsonResponse
from django.views.generic import ListView, View

from pretalx.common.mixins.views import EventPermissionRequired
from pretalx.event.models import  TeamInvite
from pretalx.submission.models import  SubmitterAccessCode, Submission, Answer
from pretalx.event.forms import TeamInviteForm

from devroom_settings.forms import DevroomTrackSettingsForm, DevroomTrackForm
from devroom_settings.models import TrackSettings

import pytz

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


class MatrixExport(EventPermissionRequired, View):
    permission_required = "orga.change_submissions"
    model = Submission

    def get(self, request, **kwargs):
        data = []

        schedule=self.request.event.wip_schedule.scheduled_talks.prefetch_related("submission__speakers").prefetch_related("submission__speakers__answers")
        for slot in schedule.all():
            # matrix tobe: s.usersettings.matrix_id if hasattr(s, "usersettings") else ""
            # for now based on question but that covers speakers only!
            persons = []
            for s in slot.submission.speakers.all():
                person_data = {
                    "person_id": s.pk,
                    "event_role": "speaker",
                    "name": s.name,
                    "email": s.email
                }

                try:
                    answer = s.answers.get(question=12).answer
                    person_data["matrix_id"] = answer
                except Answer.DoesNotExist:
                    person_data["matrix_id"] = None

                persons.append(person_data)
            talk = {"event_id": slot.submission.pk,
                    "title": slot.submission.title,
                    "persons": persons,
                    "conference_room": str(slot.room.name),
                    "start_datetime": slot.start.astimezone(pytz.timezone("Europe/Brussels")),
                    "duration": (slot.end - slot.start).total_seconds(),
                    "track_id": slot.submission.track_id}
            data.append(talk)
        return JsonResponse({"talks": data}, safe=True)

