import pghistory

from pretalx.event.models import Event, Organiser, Team, TeamInvite

## common

# tracking this is probably not useful and rather confusing
# from pretalx.common.models import ActivityLog
# @pghistory.track(
#    pghistory.Snapshot(), pghistory.BeforeDelete())
# class ActivityLogProxy(ActivityLog):
#    class Meta:
#        proxy=True


## event


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete(), exclude='updated')
class EventProxy(Event):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class OrganiserProxy(Organiser):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class TeamProxy(Team):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete(), exclude='token')
class TeamInviteProxy(TeamInvite):
    class Meta:
        proxy = True


from pretalx.mail.models import MailTemplate, QueuedMail


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class MailTemplateProxy(MailTemplate):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class QueuedMailProxy(QueuedMail):
    class Meta:
        proxy = True


from pretalx.person.models import SpeakerInformation, SpeakerProfile, User


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class SpeakerInformationProxy(SpeakerInformation):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class SpeakerProfileProxy(SpeakerProfile):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=["password"])
class UserProxy(User):
    class Meta:
        proxy = True


from pretalx.schedule.models import Room, Schedule, TalkSlot


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class RoomProxy(Room):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class ScheduleProxy(Schedule):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class TalkSlotProxy(TalkSlot):
    class Meta:
        proxy = True


from pretalx.submission.models import Answer, Review, Submission, Track


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=["invitation_token"])
class SubmissionProxy(Submission):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class ReviewProxy(Review):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class AnswerProxy(Answer):
    class Meta:
        proxy = True


@pghistory.track(pghistory.Snapshot(), pghistory.BeforeDelete())
class TrackProxy(Track):
    class Meta:
        proxy = True
