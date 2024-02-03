import json
import logging
from pathlib import Path

import pytz
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, F, Value
from django.db.models.functions import Cast
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, View
from django_scopes import scope, scopes_disabled
from pretalx.common.mixins.views import EventPermissionRequired
from pretalx.event.forms import TeamInviteForm
from pretalx.event.models import TeamInvite
from pretalx.schedule.models import Room, TalkSlot
from pretalx.submission.models import Resource, Submission, SubmitterAccessCode, Track

from devroom_settings.forms import (
    DevroomTrackForm,
    DevroomTrackSettingsForm,
    FosdemFeedbackForm,
)
from devroom_settings.models import FosdemFeedback, TrackSettings


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
            TeamInviteForm(prefix=f"invite_{track.slug}")
            for track in context["trackssettings"]
        ]

        access_codes = [
            SubmitterAccessCode.objects.filter(track=track.track).values_list(
                "code", flat=True
            )
            for track in context["trackssettings"]
        ]

        room_days = [
            get_track_room_days([track.track]) for track in context["trackssettings"]
        ]

        context["track_forms"] = zip(
            context["trackssettings"],
            forms,
            invite_forms,
            devroom_forms,
            access_codes,
            room_days,
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

            invite_form = TeamInviteForm(
                self.request.POST, prefix=f"invite_{track.slug}"
            )
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

        schedule = self.request.event.wip_schedule.scheduled_talks.prefetch_related(
            "submission__speakers"
        ).prefetch_related("submission__track__tracksettings__manager_team__members")

        for slot in schedule.all():
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
                },
            }
            data.append(talk)
        return JsonResponse({"talks": data}, safe=True)


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
    permission_required = "orga.change_submissions"

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
            resources = []
            for record in data:
                if not record["description"].startswith(VIDEO_RECORDING_STRING):
                    return JsonResponse(
                        {
                            "error": f"Invalid description, must start with '{VIDEO_RECORDING_STRING}'"
                        },
                        status=404,
                    )
                resource = Resource(
                    submission=submission,
                    link=record["link"],
                    description=record["description"],
                )
                resources.append(resource)
        except:
            logging.exception("invalid data posted to videolink")
            return JsonResponse({"error": "Invalid data"}, status=400)

        # if we end up here we assume everything is valid and we remove the existing records
        # note you can send an empty array to remove previous values

        existing_links = submission.resources.filter(
            description__startswith=VIDEO_RECORDING_STRING
        )
        count_existing = existing_links.count()
        existing_links.delete()

        # and add the new ones
        Resource.objects.bulk_create(resources)
        status = 201 if len(resources) > 0 else 200
        return JsonResponse(
            {
                "message": f"{len(resources)} links created successfully, {count_existing} removed"
            },
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
    permission_required = "orga.change_submissions"

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
            / f"fosdem-2024/video_instructions/{day}-{room}.pdf"
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
        if not self.submission.slot and self.submission.slot.start:
            raise Http404("Submission not found or not scheduled/open for feedback")
        kwargs["instance"] = FosdemFeedback(submission=self.submission)
        return kwargs

    def form_valid(self, form):
        # Set the submission before saving the form
        form.instance.submission = self.submission
        return super().form_valid(form)
