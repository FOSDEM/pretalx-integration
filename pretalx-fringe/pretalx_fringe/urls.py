from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import FringeActivityListView, FringeActivityView, FringeCreateView

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fringe/(?P<pk>\d+)/$",
        FringeActivityView.as_view(),
        name="fringe_edit",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/fringe/$",
        FringeActivityListView.as_view(),
        name="fringe_list",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/fringe/$",
        FringeCreateView.as_view(),
        name="fringe_add",
    ),
]
