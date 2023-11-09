from django.urls import path

from pretalx.event.models.event import SLUG_CHARS

from . import views

urlpatterns = [path(f"p/changelog", views.last_changes, name="changelog")]
