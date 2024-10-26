# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django_scopes import scope, scopes_disabled
from pretalx.event.models import Event, Organiser, Team
from pretalx.submission.models import Track

from devroom_settings.models import TrackSettings


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
            existing_tracks = list(Track.objects.all().values_list("name", flat=True))

        # create organiser (groups teams)
        organiser, _ = Organiser.objects.get_or_create(
            slug=dest_event.slug, name=f"{dest_event.name} teams"
        )
        organiser.save()
        organiser.events.add(dest_event)
        organiser.save()

        for i, submission in enumerate(accepted_devrooms):
            # for future: fetch answers from submission
            # for CfP
            # with scope(event=source_event):
            #    answers = submission.answers.filter()

            if submission.title in existing_tracks:
                continue
            track = Track(name=submission.title, event=dest_event)
            track.color = (
                "#6F42C1"  # not used, but otherwise it will ask when you open the page
            )
            track.position = i + len(existing_tracks)
            track.save()

            tracksetting = TrackSettings(track=track)
            tracksetting.track_type = TrackSettings.TrackType.DEVROOM

            tracksetting.slug = slugify(track.name)[0:63]
            tracksetting.mail = f"{tracksetting.slug}-devroom-manager@fosdem.org"
            print(f"adding {track.name}")

            # create manager team
            manager_team_name = f"managers-{tracksetting.slug}-{year}"
            review_team_name = f"review-{tracksetting.slug}-{year}"

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
