import datetime
import functools
import inspect

from django.apps import apps
from django.db.models.fields.related import ForeignKey
from django.utils.dateparse import parse_datetime
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


def set_extra_info(event):
    """Get extra info for a model

    Get useful data for an id, eg name or title
    for a friendlier display"""
    if "title" in event.pgh_data:
        event.extra = event.pgh_data["title"]
    elif "name" in event.pgh_data:
        event.extra = event.pgh_data["name"]


@functools.lru_cache(maxsize=1, typed=False)
def get_foreign_key_mapping():
    """
    Create a dictionary mapping foreign key database column names to their
    related models and fields.

    Returns:
        dict: A dictionary where the keys are foreign key database column names
              and the values are tuples (<related_model_class>, <model_field>).
    """
    foreign_key_mapping = {}

    # Ensure that the app registry is fully loaded
    apps.check_apps_ready()

    # Iterate over all installed models
    for model in apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, ForeignKey):
                # Get the database column name
                _, db_column_name = field.get_attname_column()
                # Map the database column name to the related model and field
                foreign_key_mapping[db_column_name] = field.related_model.__name__

    return foreign_key_mapping


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
            events = events.across(f"pretalx_auditlog.{model}")
        else:
            # a min_date is set for query performance
            if max_date:
                min_date = parse_datetime(max_date) - datetime.timedelta(minutes=30)
            else:
                min_date = datetime.datetime.now() - datetime.timedelta(minutes=30)
            events = events.filter(pgh_created_at__gt=min_date)
        # convert to list so we can edit/add some values
        events = list(events[:n])
        for ev in events:
            ev.short_model = (
                str(ev.pgh_model)
                .removesuffix("ProxyEvent")
                .removeprefix("pretalx_auditlog.")
            )

            set_extra_info(ev)

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
        return {"events": events, "form": form, "fk_map": get_foreign_key_mapping()}


class Modellog(PermissionRequired, TemplateView):
    """Show the history of a specific model"""

    permission_required = "person.is_administrator"
    template_name = "pretalx_auditlog/model-log.html"

    def get_context_data(self, **kwargs):
        id = int(self.request.GET["id"])
        model = self.request.GET["model"]
        if not model.endswith("ProxyEvent"):
            model = model + "ProxyEvent"
        events = Events.objects.filter(
            pgh_model=f"pretalx_auditlog.{model}", pgh_obj_id=id
        ).order_by("-pgh_created_at")
        # convert to list so we can edit/add some values
        events = list(events)
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

        return {"events": events}
