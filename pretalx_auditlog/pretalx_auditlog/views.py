import inspect

from django.views.generic.base import TemplateView
from pghistory.models import Events
from pretalx.common.views.mixins import PermissionRequired
from pretalx.person.models import User

import pretalx_auditlog.models as models

from .forms import Search

models = list(inspect.getmembers(models, inspect.isclass))
# returns a the list of (str, class)
# we only want the names of the proxyevent classes
model_names = [x[0] for x in models if "ProxyEvent" in x[0]]


class Changelog(PermissionRequired, TemplateView):
    permission_required = "person.is_administrator"
    template_name = "pretalx_auditlog/log.html"

    def get_context_data(self, **kwargs):
        if "n" in self.request.GET:
            n = int(self.request.GET["n"])
        else:
            n = 50
        events = Events.objects.order_by("-pgh_created_at")

        max_date = self.request.GET.get("max_date", None)
        model = self.request.GET.get("model", None)

        if max_date:
            events = events.filter(pgh_created_at__lt=max_date)
        if model and model != "All":
            events = events.filter(pgh_model=f"pretalx_auditlog.{model}")
        # convert to list so we can edit/add some values
        events = list(events[:n])
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
        form = Search(
            initial={"n": 50, "max_date": max_date, "model": model},
            model_names=model_names,
        )
        return {"events": events, "form": form}
