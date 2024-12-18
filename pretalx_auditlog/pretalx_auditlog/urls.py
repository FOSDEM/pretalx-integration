from django.urls import path
from pretalx.event.models.event import SLUG_CHARS

from . import views

urlpatterns = [
    path(f"orga/p/changelog", views.Changelog.as_view(), name="auditlog"),
    path(f"orga/p/modellog", views.Modellog.as_view(), name="modellog"),
]
