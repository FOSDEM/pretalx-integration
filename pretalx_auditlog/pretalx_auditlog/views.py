# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from pghistory.models import Events

from django.views.generic.base import TemplateView
from pretalx.common.mixins.views import EventPermissionRequired, PermissionRequired
from pretalx.person.models import User

class Changelog(PermissionRequired, TemplateView):
    permission_required = "person.is_administrator"
    template_name = "pretalx_auditlog/log.html"

    def get_context_data(self, **kwargs):

        if "n" in self.request.GET:
            n = int(self.request.GET["n"])
        else:
            n = 50
    
        events = list(Events.objects.order_by("-pgh_created_at")[:n])
        for ev in events:
            ev.short_model = str(ev.pgh_model).removesuffix("ProxyEvent").removeprefix("pretalx_auditlog.")
            if ev.pgh_context is not None:
                user = User.objects.get(pk=ev.pgh_context['user'])
                ev.user = user
        return {"content": text, "events": events}
