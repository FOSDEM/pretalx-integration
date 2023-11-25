# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView
from pghistory.models import Events
from pretalx.common.mixins.views import EventPermissionRequired, PermissionRequired
from pretalx.person.models import User

from .forms import Search


class Changelog(PermissionRequired, TemplateView):
    permission_required = "person.is_administrator"
    template_name = "pretalx_auditlog/log.html"

    def get_context_data(self, **kwargs):
        if "n" in self.request.GET:
            n = int(self.request.GET["n"])
        else:
            n = 50
        if "max_date" in self.request.GET and self.request.GET["max_date"] != "":
            max_date = self.request.GET["max_date"]
            events = list(
                Events.objects.order_by("-pgh_created_at").filter(
                    pgh_created_at__lt=max_date
                )[:n]
            )
        else:
            events = list(Events.objects.order_by("-pgh_created_at")[:n])
            max_date = None
        for ev in events:
            ev.short_model = (
                str(ev.pgh_model)
                .removesuffix("ProxyEvent")
                .removeprefix("pretalx_auditlog.")
            )
            if ev.pgh_context is not None:
                try:
                    user = User.objects.get(pk=ev.pgh_context["user"])
                    ev.user = user
                except (User.DoesNotExist, KeyError):
                    pass
        form = Search(initial={"n": 50, "max_date": max_date})
        return {"events": events, "form": form}
