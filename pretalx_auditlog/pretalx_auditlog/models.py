import pghistory
from pretalx.submission.models import Answer


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["updated"],
)
class AnswerProxy(Answer):
    class Meta:
        proxy = True


from pretalx.submission.models import AnswerOption


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class AnswerOptionProxy(AnswerOption):
    class Meta:
        proxy = True


from pretalx.submission.models import CfP


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class CfPProxy(CfP):
    class Meta:
        proxy = True


from pretalx.submission.models import Feedback


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class FeedbackProxy(Feedback):
    class Meta:
        proxy = True


from pretalx.submission.models import Question


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class QuestionProxy(Question):
    class Meta:
        proxy = True


from pretalx.submission.models import Resource


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class ResourceProxy(Resource):
    class Meta:
        proxy = True


from pretalx.submission.models import Review


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["updated"],
)
class ReviewProxy(Review):
    class Meta:
        proxy = True


from pretalx.submission.models import ReviewPhase


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class ReviewPhaseProxy(ReviewPhase):
    class Meta:
        proxy = True


from pretalx.submission.models import ReviewScore


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class ReviewScoreProxy(ReviewScore):
    class Meta:
        proxy = True


from pretalx.submission.models import ReviewScoreCategory


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class ReviewScoreCategoryProxy(ReviewScoreCategory):
    class Meta:
        proxy = True


from pretalx.submission.models import Submission


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["invitation_token", "updated"],
)
class SubmissionProxy(Submission):
    class Meta:
        proxy = True


from pretalx.submission.models import SubmissionType


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class SubmissionTypeProxy(SubmissionType):
    class Meta:
        proxy = True


from pretalx.submission.models import SubmitterAccessCode


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class SubmitterAccessCodeProxy(SubmitterAccessCode):
    class Meta:
        proxy = True


from pretalx.submission.models import Tag


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class TagProxy(Tag):
    class Meta:
        proxy = True


from pretalx.submission.models import Track


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["updated"],
)
class TrackProxy(Track):
    class Meta:
        proxy = True


from pretalx.mail.models import MailTemplate


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class MailTemplateProxy(MailTemplate):
    class Meta:
        proxy = True


from pretalx.mail.models import QueuedMail


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class QueuedMailProxy(QueuedMail):
    class Meta:
        proxy = True


from pretalx.event.models import Event


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["updated"],
)
class EventProxy(Event):
    class Meta:
        proxy = True


from pretalx.event.models import Organiser


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class OrganiserProxy(Organiser):
    class Meta:
        proxy = True


from pretalx.event.models import Team


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class TeamProxy(Team):
    class Meta:
        proxy = True


from pretalx.event.models import TeamInvite


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["token"],
)
class TeamInviteProxy(TeamInvite):
    class Meta:
        proxy = True


from pretalx.person.models import SpeakerInformation


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class SpeakerInformationProxy(SpeakerInformation):
    class Meta:
        proxy = True


from pretalx.person.models import SpeakerProfile


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class SpeakerProfileProxy(SpeakerProfile):
    class Meta:
        proxy = True


from pretalx.person.models import User


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=["password", "pw_reset_token"],
)
class UserProxy(User):
    class Meta:
        proxy = True


from pretalx.schedule.models import Availability


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class AvailabilityProxy(Availability):
    class Meta:
        proxy = True


from pretalx.schedule.models import Room


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class RoomProxy(Room):
    class Meta:
        proxy = True


from pretalx.schedule.models import Schedule


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class ScheduleProxy(Schedule):
    class Meta:
        proxy = True


from pretalx.schedule.models import TalkSlot


@pghistory.track(
    pghistory.InsertEvent(),
    pghistory.UpdateEvent(),
    pghistory.DeleteEvent(),
    exclude=[],
)
class TalkSlotProxy(TalkSlot):
    class Meta:
        proxy = True
