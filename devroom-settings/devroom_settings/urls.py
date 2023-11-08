from django.urls import include, path

from . import views


from django.urls import re_path


from pretalx.event.models.event import SLUG_REGEX


urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/devroom-report/$",
        views.DevroomReport.as_view(),
        name="devroom-report",
    ),
]
