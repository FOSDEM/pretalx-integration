from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from . import views

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/devroom-report/$",
        views.DevroomReport.as_view(),
        name="devroom-report",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/devroom-dashboard/(?P<track_slug>[a-z0-9-_]+)$",
        views.DevroomDashboard.as_view(),
        name="devroom-dashboard",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/devroom-team/(?P<track_slug>[a-z0-9-_]+)$",
        views.DevroomTeam.as_view(),
        name="devroom-team",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/track/(?P<track_id>[0-9]+)$",
        views.TrackSettingsView.as_view(),
        name="tracksettings",
    ),
    # overwrite default path of pretalx
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/cfp/tracks/(?P<track_id>[0-9]+)$",
        views.TrackSettingsView.as_view(),
        name="tracksettings",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/video-instructions/(?P<room>[a-zA-Z0-9.-]+)/(?P<day>[0-9]+)/$",
        views.VideoInstructionsView.as_view(),
        name="video-instructions",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/matrix/$",
        views.MatrixExport.as_view(),
        name="matrix-export",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/videolink/$",
        views.VideoSubmissionListView.as_view(),
        name="videolink-list",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/videolink/(?P<submission_id>\d+)/$",
        views.VideoSubmissionView.as_view(),
        name="videolink-update",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/feedback/(?P<submission_code>[A-Z0-9]+)/$",
        views.FeedbackCreateView.as_view(),
        name="fosdem_feedback",
    ),
    # overwrite the default feedback
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/talk/(?P<submission_code>[A-Z0-9]+)/feedback/$",
        views.FeedbackCreateView.as_view(),
        name="feedback",
    ),
    # feedback list
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/feedback/$",
        views.FeedbackListView.as_view(),
        name="feedback_list",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/check/$",
        views.ScheduleCheckView.as_view(),
        name="fosdem_schedule_check",
    ),
]
