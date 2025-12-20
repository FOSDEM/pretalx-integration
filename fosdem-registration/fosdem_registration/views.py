from django.core.mail import EmailMessage
from django.db.models import Count, F, IntegerField, OuterRef, Subquery
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.edit import FormView
from pretalx.common.views.mixins import EventPermissionRequired
from pretalx.event.models import Event
from pretalx.submission.models import Submission
from pretalx.submission.models.question import Answer

from .forms import (
    FosdemRegistrationForm,
    FosdemRegistrationGuardianForm,
    RegistrationFormSet,
)
from .models import FosdemRegistration, FosdemRegistrationGuardian


class RegistrationOverview(EventPermissionRequired, ListView):
    permission_required = "orga.view_fosdem_registrations"
    model = Submission

    template_name = "fosdem_registration/registration_overview.html"
    context_object_name = "submissions"

    def get_queryset(self):
        max_participants_subquery = Answer.objects.filter(
            submission=OuterRef("pk"),  # link to the submission
            question=F(
                "submission__track__fosdemregistrationtrack__max_number_question"
            ),
        ).values("answer")[
            :1
        ]  # only one answer expected
        event = Event.objects.get(slug=self.kwargs["event"])
        submissions = (
            Submission.objects.filter(
                track__fosdemregistrationtrack__isnull=False,
                state="confirmed",
                event=event,
            )
            .annotate(
                nr_registrations=Count("fosdemregistration"),
                max_number=Subquery(max_participants_subquery),
            )
            .select_related("track")
            .order_by("track__name", "title")
        )
        return submissions


class RegistrationDetail(EventPermissionRequired, ListView):
    permission_required = "orga.view_fosdem_registrations"
    model = FosdemRegistration
    template_name = "fosdem_registration/session.html"

    def get_queryset(self):
        submission = Submission.objects.get(
            code=self.kwargs["submission_code"],
            track__fosdemregistrationtrack__isnull=False,
            state="confirmed",
        )
        return submission.fosdemregistration_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = Event.objects.get(slug=self.kwargs["event"])
        submission = Submission.objects.get(
            code=self.kwargs["submission_code"],
            track__fosdemregistrationtrack__isnull=False,
            state="confirmed",
            event=event,
        )

        talkslot = submission.slots.get(schedule=event.current_schedule)
        context["talkslot"] = talkslot
        context["submission"] = submission
        context["schedule"] = submission.slots.get(schedule=event.current_schedule)
        return context


class GuardianWithRegistrationsCreateView(CreateView):
    model = FosdemRegistrationGuardian
    form_class = FosdemRegistrationGuardianForm
    template_name = "fosdem_registration/register.html"
    success_url = reverse_lazy("registration_success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        event = Event.objects.get(slug=self.kwargs["event"])

        max_participants_subquery = Answer.objects.filter(
            submission=OuterRef("pk"),  # link to the submission
            question=F(
                "submission__track__fosdemregistrationtrack__max_number_question"
            ),
        ).values("answer")[
            :1
        ]  # only one answer expected

        submissions = Submission.objects.filter(
            code=self.kwargs["submission_code"],
            track__fosdemregistrationtrack__isnull=False,
            state="confirmed",
            event=event,
        ).annotate(
            nr_registrations=Count("fosdemregistration"),
            max_number=Subquery(max_participants_subquery),
        )
        if len(submissions) != 1:
            raise Http404("Submission not found")
        submission = submissions.first()

        if self.request.POST:
            context["formset"] = RegistrationFormSet(self.request.POST)
        else:
            context["formset"] = RegistrationFormSet(
                queryset=FosdemRegistration.objects.none()
            )

        context["submission"] = submission
        context["talkslot"] = submission.slots.get(schedule=event.current_schedule)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        formset = RegistrationFormSet(
            self.request.POST,
            queryset=FosdemRegistration.objects.none(),
        )
        for subform in formset.forms:
            subform.instance.session = context["submission"]

        if formset.is_valid():
            # Save the guardian first
            guardian = form.save()

            # Save children and link to guardian
            registrations = formset.save(commit=False)
            for reg in registrations:
                reg.session = context["submission"]
                reg.registering_person = guardian
                reg.save()

            submission = registrations[0].session

            context["correct_submitted"] = True
            context["guardian_submitted"] = guardian
            context["registrations_submitted"] = registrations
            context["submission"] = submission

            mail_text = render_to_string("fosdem_registration/mail.txt", context)
            mail = EmailMessage(
                to=[guardian.email],
                from_email="FOSDEM Junior<junior-organisers@fosdem.org>",
                subject=f"FOSDEM JUNIOR registration {context['submission'].title}",
                body=mail_text,
            )
            mail.send()

        # If formset invalid, re-render page with errors
        return render(self.request, self.template_name, context)
