from django.urls import re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import SuggestCreateView, TalkSuggestionListView, TalkSuggestionView

print("***suggest url loaded")

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/suggest/(?P<pk>\d+)/$",
        TalkSuggestionView.as_view(),
        name="suggest_edit",
    ),
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/p/suggest/$",
        TalkSuggestionListView.as_view(),
        name="suggest_list",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/suggest/$",
        SuggestCreateView.as_view(),
        name="suggest_add",
    ),
]
