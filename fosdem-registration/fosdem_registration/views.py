from django.db.models import Count, F, IntegerField, OuterRef, Subquery
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic.edit import FormView
from pretalx.common.views.mixins import PermissionRequired
from pretalx.event.models import Event
from pretalx.submission.models import Submission
from pretalx.submission.models.question import Answer

from .forms import (
    FosdemRegistrationForm,
    FosdemRegistrationGuardianForm,
    RegistrationFormSet,
)
from .models import FosdemRegistration, FosdemRegistrationGuardian


class RegistrationOverview(PermissionRequired, ListView):
    permission_required = "orga.fringe_edit"
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
        submissions = (
            Submission.objects.filter(
                track__fosdemregistrationtrack__isnull=False, state="confirmed"
            )
            .annotate(
                nr_registrations=Count("fosdemregistration"),
                max_number=Subquery(max_participants_subquery),
            )
            .select_related("track")
            .order_by("track__name", "title")
        )
        return submissions


class RegistrationDetail(PermissionRequired, ListView):
    permission_required = "orga.fringe_edit"
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

        context["submission"] = submission
        context["schedule"] = submission.slots.filter(schedule=event.current_schedule)
        return context


class GuardianWithRegistrationsCreateView(CreateView):
    model = FosdemRegistrationGuardian
    form_class = FosdemRegistrationGuardianForm
    template_name = "fosdem_registration/register.html"
    success_url = reverse_lazy("registration_success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submission = Submission.objects.get(
            code=self.kwargs["submission_code"],
            track__fosdemregistrationtrack__isnull=False,
            state="confirmed",
        )
        if self.request.POST:
            context["formset"] = RegistrationFormSet(self.request.POST)
        else:
            # start with empty formset
            context["formset"] = RegistrationFormSet(
                queryset=FosdemRegistration.objects.none()
            )

        context["submission"] = submission
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        print(context)

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

            # if saved succesful - show success message
            context["correct_submitted"] = True
            context["guardian_submitted"] = guardian
            context["registrations_submitted"] = registrations

        # If formset invalid, re-render page with errors
        return render(self.request, self.template_name, context)
