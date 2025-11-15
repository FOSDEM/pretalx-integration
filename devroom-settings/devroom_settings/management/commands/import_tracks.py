# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django_scopes import scope, scopes_disabled
from i18nfield.strings import LazyI18nString
from pretalx.event.models import Event, Organiser, Team
from pretalx.submission.models import Track

from devroom_settings.models import TrackSettings


def boolean_input(question, default=None):
    result = input("%s " % question)
    if not result and default is not None:
        return default
    while len(result) < 1 or result[0].lower() not in "yn":
        result = input("Please answer yes or no: ")
    return result[0].lower() == "y"


class Command(BaseCommand):
    help = "Import accepted devrooms from another CfP as devrooms (track)"

    def add_arguments(self, parser):
        parser.add_argument("source", help="Source event slug")
        parser.add_argument("destination", help="Destination event slug")

    def handle(self, *args, **kwargs):
        source = kwargs["source"]
        source_event = Event.objects.get(slug=source)
        with scope(event=source_event):
            accepted_devrooms = source_event.submissions.filter(
                state__in=["confirmed", "accepted"]
            ).order_by("title")

        dest = kwargs["destination"]
        dest_event = Event.objects.get(slug=dest)
        year = dest[-4:]
        with scope(event=dest_event):
            nr_existing_tracks = Track.objects.all().count()
            existing_proposal_ids = list(
                Track.objects.filter(tracksettings__proposal__isnull=False).values_list(
                    "tracksettings__proposal", flat=True
                )
            )
        print(existing_proposal_ids)

        organiser = Organiser.objects.get(slug="fosdem")
        for i, submission in enumerate(accepted_devrooms):
            # for future: fetch answers from submission
            # for CfP
            with scope(event=source_event):
                slug_answers = submission.answers.filter(
                    question__question__contains="slug"
                )
            if submission.id in existing_proposal_ids:
                continue
            if not boolean_input(f"Import {submission.title}"):
                continue
            track = Track(
                name=LazyI18nString({dest_event.locale: submission.title}),
                event=dest_event,
            )
            track.color = (
                "#6F42C1"  # not used, but otherwise it will ask when you open the page
            )
            track.position = i + nr_existing_tracks
            track.save()

            tracksetting = TrackSettings(track=track)
            tracksetting.track_type = TrackSettings.TrackType.DEVROOM

            if len(slug_answers) == 1:
                slug = slugify(slug_answers[0].answer)
            else:
                slug = slugify(track.name)[0:63]
            tracksetting.slug = slug
            tracksetting.mail = f"{slug}-devroom-manager@fosdem.org"
            tracksetting.proposal = submission
            print(f"adding {track.name} ({slug})")

            # create manager team
            manager_team_name = f"managers-{slug}-{year}"
            review_team_name = f"review-{slug}-{year}"

            manager_team = Team(
                name=manager_team_name,
                organiser=organiser,
                is_reviewer=True,
                can_change_submissions=True,
            )
            review_team = Team(
                name=review_team_name, organiser=organiser, is_reviewer=True
            )
            manager_team.save()
            review_team.save()

            manager_team.limit_events.set([dest_event])
            review_team.limit_events.set([dest_event])
            with scope(event=dest_event):
                manager_team.limit_tracks.set([track])
                review_team.limit_tracks.set([track])

            tracksetting.manager_team = manager_team
            tracksetting.review_team = review_team
            tracksetting.save()

            for user in submission.speakers.all():
                manager_team.members.add(user)
            manager_team.save()
