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
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/devroom-dashboard/$",
        views.DevroomDashboard.as_view(),
        name="devroom-dashboard",
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
]
