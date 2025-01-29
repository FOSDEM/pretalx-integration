import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, View
from django.views.generic.edit import UpdateView
from pretalx.common.views.mixins import PermissionRequired
from pretalx.mail.models import QueuedMail

from .forms import TalkSuggestionForm
from .models import TalkSuggestion

logger = logging.getLogger(__name__)


class TalkSuggestionView(PermissionRequired, UpdateView):
    permission_required = "orga.suggest_edit"
    model = TalkSuggestion
    form_class = TalkSuggestionForm
    template_name = "pretalx_suggest/activity_edit.html"

    def get_success_url(self):
        # return reverse_lazy('plugins: pretalx_suggest:suggest_list', kwargs={'event': self.request.event.slug})
        return f"/orga/event/{self.request.event.slug}/p/suggest"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass the user to the form
        kwargs["admin"] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin"] = True
        return context

    def form_valid(self, form):
        # Save the updated activity
        logger.debug("Updating suggestion: %s", form.cleaned_data)
        form.instance.user = self.request.user  # Ensure the user is linked
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle form errors
        logger.error("Form errors: %s", form.errors)
        return super().form_invalid(form)


class TalkSuggestionListView(PermissionRequired, ListView):
    permission_required = "orga.suggest_edit"
    model = TalkSuggestion

    template_name = "pretalx_suggest/list.html"  # Specify your template
    context_object_name = "suggestions"  # Name for the context in the template

    def get_queryset(self):
        return TalkSuggestion.objects.all()


class SuggestCreateView(LoginRequiredMixin, CreateView):
    model = TalkSuggestion
    form_class = TalkSuggestionForm
    template_name = "pretalx_suggest/suggestion.html"
    success_url = "https://fosdem.org/2025/suggest/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        logger.debug("Form is valid: %s", form.cleaned_data)
        form.instance.user = self.request.user
        logger.debug(form.instance)
        super().form_valid(form)
        form.save()
        self.sendmail(form)
        return render(
            self.request, "pretalx_suggest/thanks.html", {"event": self.request.event}
        )

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
            A new suggest submission was made

            Name: {name}

            Why: {why}

            speaker_connection: {speaker_connection}

            Contact: {contact}

            Other: {other}

            Submitter: {submitter}
            """.format(
            name=form.cleaned_data.get("name"),
            why=form.cleaned_data.get("why"),
            contact=form.cleaned_data.get("contact"),
            speaker_connection=form.cleaned_data.get("speaker_connection"),
            other=form.cleaned_data.get("other"),
            submitter=f"{self.request.user.name}<{self.request.user.email}>",
        )
        name = form.cleaned_data.get("name")
        mail = QueuedMail.objects.create(
            subject=f"new main track suggestion: {name}",
            text=message,
            to=f"program@fosdem.org, {self.request.user.email}",
        )
        mail.send()
