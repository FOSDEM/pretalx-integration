# craete teams for every devroom

from django.core.management.base import BaseCommand
from django_scopes import scopes_disabled
from pretalx.person.models import User, SpeakerProfile
from pretalx.event.models import Team, TeamInvite
from pretalx.submission.models import Answer, Submission


def print_user_info(user):
    print(f"{user.name} - {user.email} - last-login: {user.last_login}")
    teams = [str(team) for team in user.teams.all()]
    teams = ",".join(teams)
    print(f"Teams: {teams}")
    with scopes_disabled():
        #profiles = ",".join(user.profiles.all())
        print("Submissions:")
        for submission in user.submissions.all():
            print(f"- {submission.title}({submission.event.name})")


def merge_users(user1, user2, interactive=True):
    """Merge all info of user2 on user 1"""

    teams = Team.objects.filter(members=user2)

    for team in teams:
        team.members.add(user1)
        team.members.remove(user2)

    with scopes_disabled():
        submissions = Submission.objects.filter(speakers=user2)
        for submission in submissions:
            submission.speakers.add(user1)
            submission.speakers.remove(user2)
        Answer.objects.filter(person=user2).update(person=user1)

        user1_profile_events = {sp.event: sp for sp in SpeakerProfile.objects.filter(speakers=user1)}
        profiles = SpeakerProfile.objects.filter(speakers=user2).exclude(biography=None)
        for profile in profiles:
            if profile.event not in user1_profile_events:
                profile.update(user=user1)
            else:
                print(f"bios for {profile.event}")
                print(f"user1:\n{user1_profile_events[profile.event].biography}")
                print("f:user2:\n{profile.biography}")
                while True:
                    res=input("Keep 1 or 2?")
                    if res in ["1", "2"]:
                        break
                    else:
                        print("enter 1 or 2")
                if res == "1":
                    profile.delete()
                if res == "2":
                    user1_profile_events[profile.event].delete()
                    profile.update(user=user1)





    user2.shred()

class Command(BaseCommand):
    help = "Merge two users"

    def add_arguments(self, parser):
        parser.add_argument("user1", help="First user code, eg XWDLEB")
        parser.add_argument("user2", help="Second user code, eg WY7TVG")

    def handle(self, *args, **kwargs):
        user1 = User.objects.get(code=kwargs["user1"])
        user2 = User.objects.get(code=kwargs["user2"])

        print("User 1")
        print_user_info(user1)
        print("User 2")
        print_user_info(user2)

        print("Move all to User 1?")
        merge_users(user1, user2)
        print_user_info(user1)








