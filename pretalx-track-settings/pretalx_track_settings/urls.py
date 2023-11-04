from django.urls import include, path

from pretalx.event.models.event import SLUG_CHARS

from . import views

urlpatterns = [
    path(f'orga/event/<str:event>/p/cfp/tracks/<int:pk>/',
        views.TrackDetail.as_view(), name='backend')
    ]