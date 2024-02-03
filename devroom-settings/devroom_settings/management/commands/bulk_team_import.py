# import accepted devrooms from another CfP as tracks

from django.core.management.base import BaseCommand
from pretalx.event.models import Team, TeamInvite


class Command(BaseCommand):
    help = "Bulk import team members"

    def add_arguments(self, parser):
        parser.add_argument("team_id", help="team id")
        parser.add_argument("mail", help="mail of person to be invited")

    def handle(self, *args, **kwargs):
        team_id = kwargs["team_id"]
        mail = kwargs["mail"]
        team = Team.objects.get(pk=team_id)
        print(f"inviting {mail} to team {team.name}")
        invite = TeamInvite(email=mail, team=team)
        invite.send()
        invite.save()
