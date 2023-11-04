
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
#     template_name = "pretalx_track_settings/form_fragment.html"
#     permission_required = "orga.view_track"
#     write_permission_required = "orga.edit_track"


class TrackDetail(PermissionRequired, ActionFromUrl, CreateOrUpdateView):
    model = Track
    form_class = TrackSettingsForm
    template_name = "pretalx_track_settings/track_form.html"
    permission_required = "orga.view_track"
    write_permission_required = "orga.edit_track"

    def get_success_url(self) -> str:
        return self.request.event.cfp.urls.tracks

    def get_object(self):
        return self.request.event.tracks.filter(pk=self.kwargs.get("pk")).first()

    def get_permission_object(self):
        return self.get_object() or self.request.event

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["event"] = self.request.event
        return result

    def form_valid(self, form):
        form.instance.event = self.request.event
        result = super().form_valid(form)

        messages.success(self.request, _("The track has been saved."))
        if form.has_changed():
            action = "pretalx.track." + ("update" if self.object else "create")
            form.instance.log_action(action, person=self.request.user, orga=True)
        return result
