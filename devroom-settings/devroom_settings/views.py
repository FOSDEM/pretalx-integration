
from .models import TrackSettings
from .forms import TrackSettingsForm

from pretalx.submission.models import Track
from pretalx.common.views import CreateOrUpdateView, OrderModelView
from pretalx.common.mixins.views import (
    ActionFromUrl,
    PermissionRequired,
)

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
# class TrackSettingsDetail(PermissionRequired, ActionFromUrl, CreateOrUpdateView):
#     model = TrackSettings
#     form_class = TrackSettingForm
#     template_name = "devroom_settings/form_fragment.html"
#     permission_required = "orga.view_track"
#     write_permission_required = "orga.edit_track"

