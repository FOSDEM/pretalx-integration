import pghistory
from pretalx.submission.models import Answer

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['updated'])
class AnswerProxy(Answer):
    class Meta:
        proxy=True

from pretalx.submission.models import AnswerOption

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class AnswerOptionProxy(AnswerOption):
    class Meta:
        proxy=True

from pretalx.submission.models import CfP

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class CfPProxy(CfP):
    class Meta:
        proxy=True

from pretalx.submission.models import Feedback

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class FeedbackProxy(Feedback):
    class Meta:
        proxy=True

from pretalx.submission.models import Question

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class QuestionProxy(Question):
    class Meta:
        proxy=True

from pretalx.submission.models import Resource

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ResourceProxy(Resource):
    class Meta:
        proxy=True

from pretalx.submission.models import Review

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['updated'])
class ReviewProxy(Review):
    class Meta:
        proxy=True

from pretalx.submission.models import ReviewPhase

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ReviewPhaseProxy(ReviewPhase):
    class Meta:
        proxy=True

from pretalx.submission.models import ReviewScore

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ReviewScoreProxy(ReviewScore):
    class Meta:
        proxy=True

from pretalx.submission.models import ReviewScoreCategory

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ReviewScoreCategoryProxy(ReviewScoreCategory):
    class Meta:
        proxy=True

from pretalx.submission.models import Submission

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['invitation_token'])
class SubmissionProxy(Submission):
    class Meta:
        proxy=True

from pretalx.submission.models import SubmissionType

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class SubmissionTypeProxy(SubmissionType):
    class Meta:
        proxy=True

from pretalx.submission.models import SubmitterAccessCode

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class SubmitterAccessCodeProxy(SubmitterAccessCode):
    class Meta:
        proxy=True

from pretalx.submission.models import Tag

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class TagProxy(Tag):
    class Meta:
        proxy=True

from pretalx.submission.models import Track

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class TrackProxy(Track):
    class Meta:
        proxy=True

from pretalx.common.models import ActivityLog

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ActivityLogProxy(ActivityLog):
    class Meta:
        proxy=True

from pretalx.mail.models import MailTemplate

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class MailTemplateProxy(MailTemplate):
    class Meta:
        proxy=True

from pretalx.mail.models import QueuedMail

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class QueuedMailProxy(QueuedMail):
    class Meta:
        proxy=True

from pretalx.event.models import Event

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['updated'])
class EventProxy(Event):
    class Meta:
        proxy=True

from pretalx.event.models import Organiser

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class OrganiserProxy(Organiser):
    class Meta:
        proxy=True

from pretalx.event.models import Team

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class TeamProxy(Team):
    class Meta:
        proxy=True

from pretalx.event.models import TeamInvite

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['token'])
class TeamInviteProxy(TeamInvite):
    class Meta:
        proxy=True

from pretalx.person.models import SpeakerInformation

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class SpeakerInformationProxy(SpeakerInformation):
    class Meta:
        proxy=True

from pretalx.person.models import SpeakerProfile

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class SpeakerProfileProxy(SpeakerProfile):
    class Meta:
        proxy=True

from pretalx.person.models import User

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=['password'])
class UserProxy(User):
    class Meta:
        proxy=True

from pretalx.schedule.models import Availability

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class AvailabilityProxy(Availability):
    class Meta:
        proxy=True

from pretalx.schedule.models import Room

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class RoomProxy(Room):
    class Meta:
        proxy=True

from pretalx.schedule.models import Schedule

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class ScheduleProxy(Schedule):
    class Meta:
        proxy=True

from pretalx.schedule.models import TalkSlot

@pghistory.track(
    pghistory.Snapshot(), pghistory.BeforeDelete(), exclude=[])
class TalkSlotProxy(TalkSlot):
    class Meta:
        proxy=True

