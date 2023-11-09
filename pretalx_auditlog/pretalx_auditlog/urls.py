from django.urls import path

from pretalx.event.models.event import SLUG_CHARS

from . import views

urlpatterns = [path(f"p/changelog", views.Changelog.as_view(), name="changelog")]
