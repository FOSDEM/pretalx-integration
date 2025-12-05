import collections
import json
import logging
from pathlib import Path

import pytz
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, F, Value
from django.db.models.functions import Cast
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, TemplateView, View
from django_context_decorator import context
from django_scopes import scope, scopes_disabled
from pretalx.common.views.mixins import EventPermissionRequired
from pretalx.event.forms import TeamInviteForm
from pretalx.event.models import TeamInvite
from pretalx.schedule.models import Room, TalkSlot
from pretalx.schedule.utils import guess_schedule_version
from pretalx.submission.models import Resource, Submission, SubmitterAccessCode, Track

from devroom_settings.forms import (
    DevroomTrackForm,
    DevroomTrackSettingsForm,
    FosdemFeedbackForm,
    TrackForm,
    TrackSettingsForm,
)
from devroom_settings.models import FosdemFeedback, RoomSettings, TrackSettings


class TrackSettings(EventPermissionRequired, TemplateView):
    permission_required = "event.update_event"
    template_name = "devroom_settings/tracksettings.html"

    def get(self, request, *args, **kwargs):
        track = Track.objects.get(pk=kwargs["track_id"])
        tracksettings = track.tracksettings

        context = {
            "track": track,
            "tracksettings": tracksettings,
            "track_form": TrackForm(instance=track),
            "tracksettings_form": TrackSettingsForm(instance=tracksettings),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        track = Track.objects.get(pk=kwargs["track_id"])
        tracksettings = track.tracksettings

        track_form = TrackForm(request.POST, instance=track)
        tracksettings_form = TrackSettingsForm(request.POST, instance=tracksettings)

        if track_form.is_valid() and tracksettings_form.is_valid():
            track_form.save()
            tracksettings_form.track = track
            tracksettings_form.save()
            return redirect(request.path)

        context = {
            "track": track,
            "tracksettings": tracksettings,
            "track_form": track_form,
            "tracksettings_form": tracksettings_form,
        }
        return self.render_to_response(context)


class DevroomReport(EventPermissionRequired, ListView):
    permission_required = "submission.orga_update_submission"
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


class DevroomTeam(EventPermissionRequired, TemplateView):
    permission_required = "submission.orga_update_submission"
    template_name = "devroom_settings/team.html"
    model = TrackSettings

    def get_queryset(self):
        teams = self.request.user.teams.all()
        track_slug = self.kwargs["track_slug"]
        return get_object_or_404(
            TrackSettings.objects.select_related(
                "track", "review_team"
            ).prefetch_related(
                "review_team__members", "manager_team", "manager_team__members"
            ),
            manager_team__in=teams,
            track__event=self.request.event,
            slug=track_slug,
        )

    def post(self, request, *args, **kwargs):
        tracksettings = self.get_queryset()
        tracksettings.track

        invite_form = TeamInviteForm(self.request.POST, prefix=f"invite")
        if invite_form.is_valid():
            invite = TeamInvite.objects.create(
                team=tracksettings.review_team,
                email=invite_form.cleaned_data["email"].lower().strip(),
            )
            invite.send()

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tracksettings = self.get_queryset()
        track = tracksettings.track
        context["track"] = track
        context["tracksettings"] = tracksettings
        context["invite_form"] = TeamInviteForm(prefix=f"invite")
        return context


class DevroomDashboard(EventPermissionRequired, TemplateView):
    permission_required = "submission.orga_update_submission"
    template_name = "devroom_settings/devroom-dashboard.html"
    model = TrackSettings

    def get_queryset(self):
        teams = self.request.user.teams.all()
        track_slug = self.kwargs["track_slug"]
        return get_object_or_404(
            TrackSettings.objects.select_related(
                "track", "review_team"
            ).prefetch_related(
                "review_team__members", "manager_team", "manager_team__members"
            ),
            manager_team__in=teams,
            track__event=self.request.event,
            slug=track_slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tracksettings = self.get_queryset()
        track = tracksettings.track
        context["track"] = track
        context["tracksettings"] = tracksettings
        context["track_settings_form"] = DevroomTrackSettingsForm(
            instance=tracksettings
        )
        context["track_form"] = DevroomTrackForm(prefix=f"track", instance=track)

        # Access codes
        context["access_codes"] = SubmitterAccessCode.objects.filter(
            track=track
        ).values_list("code", flat=True)

        return context

    def post(self, request, *args, **kwargs):
        tracksettings = self.get_queryset()
        track = tracksettings.track

        form = DevroomTrackSettingsForm(self.request.POST, instance=tracksettings)
        if form.is_valid() and form.has_changed():
            form.save()

        form = DevroomTrackForm(self.request.POST, prefix=f"track", instance=track)
        if form.is_valid() and form.has_changed():
            form.save()

        invite_form = TeamInviteForm(self.request.POST, prefix=f"invite")
        if invite_form.is_valid():
            invite = TeamInvite.objects.create(
                team=track.review_team,
                email=invite_form.cleaned_data["email"].lower().strip(),
            )
            invite.send()

        return self.get(request, *args, **kwargs)


class MatrixExport(EventPermissionRequired, View):
    permission_required = "submission.orga_update_submission"
    model = Submission

    def get(self, request, **kwargs):
        talks = []

        track_room = {}

        schedule = self.request.event.wip_schedule.scheduled_talks.prefetch_related(
            "submission__speakers"
        ).prefetch_related("submission__track__tracksettings__manager_team__members")

        for slot in schedule.all():
            if slot.submission.track.tracksettings.track_type not in [
                "MT",
                "K",
                "LT",
                "D",
            ]:
                continue

            persons = []
            for s in slot.submission.speakers.all():
                person_data = {
                    "person_id": s.pk,
                    "event_role": "speaker",
                    "name": s.name,
                    "email": s.email,
                    "matrix_id": s.matrix_id,
                }
                persons.append(person_data)
            for s in slot.submission.track.tracksettings.manager_team.members.all():
                person_data = {
                    "person_id": s.pk,
                    "event_role": "coordinator",
                    "name": s.name,
                    "email": s.email,
                    "matrix_id": s.matrix_id,
                }
                persons.append(person_data)

            duration = slot.submission.duration
            if duration is None:
                duration = (slot.end - slot.start).seconds // 60
            talk = {
                "event_id": slot.submission.pk,
                "title": slot.submission.title,
                "persons": persons,
                "conference_room": str(slot.room.name),
                "start_datetime": slot.start.astimezone(
                    pytz.timezone("Europe/Brussels")
                ),
                "duration": duration,
                "track": {
                    "id": slot.submission.track.pk,
                    "slug": slot.submission.track.tracksettings.slug,
                    "email": slot.submission.track.tracksettings.mail,
                    "name": str(slot.submission.track.name),
                    "online_qa": slot.submission.track.tracksettings.online_qa,
                },
            }
            talks.append(talk)
            track_room[slot.submission.track.tracksettings.slug] = str(slot.room.name)

        track_objects = (
            self.request.event.tracks.filter(
                tracksettings__track_type__in=["MT", "K", "LT", "D"]
            )
            .select_related("tracksettings")
            .prefetch_related("tracksettings__manager_team__members")
        )
        print(track_room)
        tracks = []
        for t in track_objects:
            persons = []
            for p in t.tracksettings.manager_team.members.all():
                person_data = {
                    "person_id": p.pk,
                    "event_role": "coordinator",
                    "name": p.name,
                    "email": p.email,
                    "matrix_id": p.matrix_id,
                }
                persons.append(person_data)
            tracks.append(
                {
                    "id": t.id,
                    "slug": t.tracksettings.slug,
                    "name": str(t.name),
                    "email": t.tracksettings.mail,
                    "online_qa": t.tracksettings.online_qa,
                    "room": track_room.get(t.tracksettings.slug),
                    "type": t.tracksettings.get_track_type_display(),
                    "managers": persons,
                }
            )

        return JsonResponse({"talks": talks, "tracks": tracks}, safe=True)


VIDEO_RECORDING_STRING = "Video recording"


class VideoSubmissionListView(View):
    def get(self, request, **kwargs):
        schedule = request.event.wip_schedule
        talks = schedule.scheduled_talks.prefetch_related("submission__resources").all()
        result = []
        for talk in talks:
            video_links = [
                {"link": link.link, "description": link.description}
                for link in talk.submission.resources.filter(
                    description__startswith=VIDEO_RECORDING_STRING
                )
            ]
            result.append(
                {
                    "id": talk.submission.pk,
                    "title": talk.submission.title,
                    "video_links": video_links,
                }
            )
        return JsonResponse(result, safe=False, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class VideoSubmissionView(EventPermissionRequired, View):
    permission_required = "submission.orga_update_submission"

    def post(self, request, submission_id, **kwargs):
        """Add or overwrite video links
        expects a list of video links + their description
        [{"description": "Video recording (WebM/VP9, 54M)", "link": "https://video.fosdem.org/2023/Janson/closing_fosdem.webm"}]
        """

        try:
            submission = request.event.talks.get(pk=int(submission_id))
        except Submission.DoesNotExist:
            return JsonResponse(
                {"error": "Invalid submission ID. Please provide a valid integer."},
                status=404,
            )

        try:
            data = json.loads(request.body)
            for record in data:
                if not record["description"].startswith(VIDEO_RECORDING_STRING):
                    return JsonResponse(
                        {
                            "error": f"Invalid description, must start with '{VIDEO_RECORDING_STRING}'"
                        },
                        status=404,
                    )
                if not record["link"].startswith("https://video.fosdem.org"):
                    return JsonResponse(
                        {
                            "error": f"Invalid link, must be https://video.fosdem.org/..."
                        },
                        status=404,
                    )

        except:
            logging.exception("invalid data posted to videolink")
            return JsonResponse({"error": "Invalid data"}, status=400)

        # if we end up here we assume everything is valid and we remove the existing records
        # note you can send an empty array to remove previous values
        links_to_remove = submission.resources.filter(
            description__startswith=VIDEO_RECORDING_STRING
        ).exclude(link__in=[i["link"] for i in data])

        nr_deleted, _ = links_to_remove.delete()
        nr_saved = 0
        # and add the new ones
        for record in data:
            resource, _ = Resource.objects.filter(
                description__startswith=VIDEO_RECORDING_STRING
            ).get_or_create(link=record["link"], submission=submission)
            if resource.description != record["description"]:
                resource.description = record["description"]
                resource.save()
                nr_saved += 1
        status = 201 if nr_saved + nr_deleted > 0 else 200
        return JsonResponse(
            {"message": f"{nr_saved} links created successfully, {nr_deleted} removed"},
            status=status,
        )

    def get(self, request, submission_id, **kwargs):
        if not Submission.objects.filter(pk=submission_id).exists():
            return JsonResponse(
                {"error": "Invalid submission ID. Please provide a valid integer."},
                status=404,
            )

        try:
            resources = Resource.objects.get(
                description__startswith=VIDEO_RECORDING_STRING, submission=submission_id
            )
            data = [
                {"description": str(r.description), "link": str(r.link)}
                for r in resources
            ]
        except Resource.DoesNotExist:
            data = []
        return JsonResponse(data, safe=False, status=200)


def get_track_room_days(tracks):
    with scopes_disabled():
        day_rooms = (
            TalkSlot.objects.filter(submission__track__in=tracks, room__isnull=False)
            .values_list("start__date__iso_week_day", "room__name")
            .distinct()
        )
        day_rooms = list(day_rooms)
        day_rooms = {(day - 5, room.localize("en")) for (day, room) in day_rooms}

    return day_rooms


class VideoInstructionsView(EventPermissionRequired, View):
    permission_required = "submission.orga_update_submission"

    def get(self, request, room, day, **kwargs):
        teams = self.request.user.teams.all()
        tracks = Track.objects.filter(
            tracksettings__manager_team__in=teams, event=self.request.event
        )
        day_rooms = get_track_room_days(tracks)

        if not (int(day), room) in day_rooms:
            msg = f"{day}, {room} supplied, not part of {day_rooms}"
            print(msg)
            raise PermissionDenied(msg)

        file_path = (
            Path(settings.MEDIA_ROOT)
            / f"{self.request.event.slug}/video_instructions/{day}-{room}.pdf"
        )
        if not file_path.exists():
            return HttpResponse("File not found", status=404)
        file = open(file_path, "rb")
        response = FileResponse(file)

        # Set the content type for the response
        response["Content-Type"] = "application/pdf"

        # Set the Content-Disposition header to force download
        response["Content-Disposition"] = f'attachment; filename="{file_path.name}"'

        return response


class FeedbackCreateView(CreateView):
    model = FosdemFeedback
    form_class = FosdemFeedbackForm
    template_name = "devroom_settings/feedback_template.html"

    def dispatch(self, request, *args, **kwargs):
        # Access the 'submission_code' from self.kwargs
        submission_code = kwargs.get("submission_code")
        self.submission = get_object_or_404(Submission, code=submission_code)

        talk = self.submission
        if talk and request.user in talk.speakers.all():
            return render(
                self.request,
                "devroom_settings/feedback_result.html",
                context={
                    "talk": talk,
                    "feedbacks": FosdemFeedback.objects.filter(submission=talk.pk),
                },
            )

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        # Redirect to a success page or adjust as needed
        return f"https://fosdem.org/schedule/event/{self.submission.slots.first().frab_slug}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = self.submission.slots.first()
        day = slot.start.astimezone(pytz.timezone("Europe/Brussels")).strftime("%a")
        start = slot.start.astimezone(pytz.timezone("Europe/Brussels")).strftime(
            "%H:%M"
        )
        end = slot.end.astimezone(pytz.timezone("Europe/Brussels")).strftime("%H:%M")
        context["talk"] = self.submission
        context["fosdem_url"] = self.get_success_url()
        context["time_room"] = f"{day} {start}-{end}, {slot.room.description}"
        speakers = [speaker.name for speaker in self.submission.speakers.all()]
        context["speakers"] = ", ".join(speakers)

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not self.submission.slot or not self.submission.slot.start:
            raise Http404("Submission not found or not scheduled/open for feedback")
        kwargs["instance"] = FosdemFeedback(submission=self.submission)
        return kwargs

    def form_valid(self, form):
        # Set the submission before saving the form
        form.instance.submission = self.submission
        return super().form_valid(form)


class ScheduleCheckView(EventPermissionRequired, TemplateView):
    permission_required = "schedule.release_schedule"
    template_name = "check.html"

    @context
    def warnings(self):
        all_warnings = self.request.event.wip_schedule.warnings
        # restructure talk warnings by type
        talk_warnings = all_warnings["talk_warnings"]
        talk_warnings_type = collections.defaultdict(list)
        for talk_warning in talk_warnings:
            warnings = talk_warning["warnings"]
            for warning in warnings:
                warning["talk_orig"] = talk_warning["talk"]
                talk_warnings_type[warning["type"]].append(warning)
        all_warnings["talk_warnings_type"] = dict(talk_warnings_type)
        return self.request.event.wip_schedule.warnings


class FeedbackListView(EventPermissionRequired, ListView):
    permission_required = "submission.orga_update_submission"
    model = FosdemFeedback
    template_name = "feedback_list.html"
    context_object_name = "feedback_list"
    ordering = ["-timestamp"]  # Show latest feedback first

    def get_queryset(self):
        teams = self.request.user.teams.all()
        tracks = Track.objects.filter(
            tracksettings__manager_team__in=teams, event=self.request.event
        )

        objects = FosdemFeedback.objects.filter(submission__track__in=tracks)
        if self.request.user.is_administrator:
            objects = FosdemFeedback.objects.filter(
                submission__event=self.request.event
            )
        return objects.order_by("timestamp")
