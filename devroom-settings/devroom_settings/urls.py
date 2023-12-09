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
]
