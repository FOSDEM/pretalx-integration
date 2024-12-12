import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView
from django.views.generic.edit import UpdateView
from pretalx.common.views.mixins import PermissionRequired
from pretalx.mail.models import QueuedMail

from .forms import FringeActivityForm
from .models import FringeActivity

logger = logging.getLogger(__name__)


class FringeActivityView(PermissionRequired, UpdateView):
    permission_required = "orga.fringe_edit"
    model = FringeActivity
    form_class = FringeActivityForm
    template_name = "pretalx_fringe/activity_edit.html"

    def get_success_url(self):
        # return reverse_lazy('plugins: pretalx_fringe:fringe_list', kwargs={'event': self.request.event.slug})
        return f"/orga/event/{self.request.event.slug}/p/fringe"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.request.event  # Pass the event to the form
        kwargs["user"] = self.request.user  # Pass the user to the form
        kwargs["admin"] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.request.event  # Pass the event to the context
        context["admin"] = True
        return context

    def form_valid(self, form):
        # Save the updated activity
        logger.debug("Updating activity: %s", form.cleaned_data)
        form.instance.event = self.request.event  # Ensure the event is linked
        form.instance.user = self.request.user  # Ensure the user is linked
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle form errors
        logger.error("Form errors: %s", form.errors)
        return super().form_invalid(form)


class FringeActivityListView(PermissionRequired, ListView):
    permission_required = "orga.fringe_edit"
    model = FringeActivity

    template_name = "fringe_list.html"  # Specify your template
    context_object_name = "fringe_activities"  # Name for the context in the template

    def get_queryset(self):
        return FringeActivity.objects.filter(event=self.request.event)


class FringeCreateView(LoginRequiredMixin, CreateView):
    model = FringeActivity
    form_class = FringeActivityForm
    template_name = "activity.html"
    success_url = "https://fosdem.org/2025/fringe/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event"] = self.request.event
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        logger.debug("Form is valid: %s", form.cleaned_data)
        form.instance.event = self.request.event
        form.instance.user = self.request.user
        logger.debug(form.instance)
        response = super().form_valid(form)
        self.sendmail(form)
        return response

    def get_login_url(self):
        login = f"/{self.request.event.slug}/login"
        # self.request.event.orga_urls.login
        return login

    def form_invalid(self, form):
        logger.error("Form errors: %s", form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.request.event
        context["admin"] = False
        return context

    def sendmail(self, form):
        message = """
            A new fringe submission was made

            Name: {name}

            Location: {location}

            Description: {description}

            Why: {why}

            URL: {url}

            Starts: {start}

            Ends: {ends}

            Cost: {cost}

            Registration: {registration}

            Contact: {contact}
            """.format(
            name=form.cleaned_data.get("name"),
            location=form.cleaned_data.get("location"),
            description=form.cleaned_data.get("description"),
            why=form.cleaned_data.get("why"),
            url=form.cleaned_data.get("url"),
            start=form.cleaned_data.get("starts"),
            ends=form.cleaned_data.get("ends"),
            cost=form.cleaned_data.get("cost"),
            registration=form.cleaned_data.get("registration"),
            contact=form.cleaned_data.get("contact"),
        )
        name = form.cleaned_data.get("name")
        mail = QueuedMail.objects.create(
            event=self.request.event,
            subject=f"new fringe submission: {name}",
            text=message,
            to=f"fringe@fosdem.org, {form.cleaned_data.get('contact')}",
        )
        mail.send()
