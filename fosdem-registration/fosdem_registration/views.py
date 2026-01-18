import logging

from django.core.mail import EmailMessage
from django.db.models import Count, F, IntegerField, OuterRef, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
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

logger = logging.getLogger(__name__)


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
        submission = get_object_or_404(
            Submission,
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

        talkslot = submission.slots.get(schedule=event.wip_schedule)
        context["talkslot"] = talkslot
        context["submission"] = submission
        context["schedule"] = submission.slots.get(schedule=event.wip_schedule)
        return context


class GuardianWithRegistrationsCreateView(CreateView):
    model = FosdemRegistrationGuardian
    form_class = FosdemRegistrationGuardianForm
    template_name = "fosdem_registration/register.html"
    success_url = reverse_lazy("registration_success")

    def get_context_data(self, **kwargs):
        logger.debug("GuardianWithRegistrationsCreateView.get_context_data called")
        context = super().get_context_data(**kwargs)

        event_slug = self.kwargs.get("event")
        submission_code = self.kwargs.get("submission_code")
        logger.debug(f"  Looking for event: {event_slug}")
        logger.debug(f"  Looking for submission: {submission_code}")

        try:
            event = Event.objects.get(slug=event_slug)
            logger.debug(f"  Found event: {event} (id={event.pk})")
        except Event.DoesNotExist:
            logger.error(f"  Event not found with slug: {event_slug}")
            raise Http404(f"Event not found: {event_slug}")

        max_participants_subquery = Answer.objects.filter(
            submission=OuterRef("pk"),  # link to the submission
            question=F(
                "submission__track__fosdemregistrationtrack__max_number_question"
            ),
        ).values("answer")[
            :1
        ]  # only one answer expected

        logger.debug("  Querying for submissions...")
        submissions = Submission.objects.filter(
            code=submission_code,
            track__fosdemregistrationtrack__isnull=False,
            state="confirmed",
            event=event,
        ).annotate(
            nr_registrations=Count("fosdemregistration"),
            max_number=Subquery(max_participants_subquery),
        )

        logger.debug(f"  Found {submissions.count()} submissions")

        if len(submissions) != 1:
            logger.error(f"  Expected 1 submission, found {len(submissions)}")
            raise Http404("Submission not found")

        submission = submissions.first()
        logger.debug(
            f"  Submission: {submission} (code={submission.code}, track={submission.track})"
        )

        if self.request.POST:
            logger.debug("  Creating formset from POST data")
            context["formset"] = RegistrationFormSet(self.request.POST)
        else:
            logger.debug("  Creating empty formset")
            context["formset"] = RegistrationFormSet(
                queryset=FosdemRegistration.objects.none()
            )

        context["submission"] = submission

        try:
            talkslot = submission.slots.get(schedule=event.current_schedule)
            context["talkslot"] = talkslot
            logger.debug(f"  Found talkslot: {talkslot}")
        except Exception as e:
            logger.error(f"  Error getting talkslot: {e}")
            raise

        logger.debug("  get_context_data completed successfully")
        return context

    def form_valid(self, form):
        logger.debug("GuardianWithRegistrationsCreateView.form_valid called")
        context = self.get_context_data()
        formset = context["formset"]

        logger.debug("  Creating new formset from POST data")
        formset = RegistrationFormSet(
            self.request.POST,
            queryset=FosdemRegistration.objects.none(),
        )

        logger.debug(f"  Formset has {len(formset.forms)} forms")
        for i, subform in enumerate(formset.forms):
            subform.instance.session = context["submission"]
            logger.debug(f"  Form {i}: setting session to {context['submission']}")

        if formset.is_valid():
            logger.debug("  Formset is valid, saving...")
            # Save the guardian first
            guardian = form.save()
            logger.debug(f"  Guardian saved: {guardian}")

            # Save children and link to guardian
            registrations = formset.save(commit=False)
            logger.debug(f"  Saving {len(registrations)} registrations")

            for i, reg in enumerate(registrations):
                reg.session = context["submission"]
                reg.registering_person = guardian
                reg.save()
                logger.debug(f"  Registration {i} saved: {reg}")

            submission = registrations[0].session

            context["correct_submitted"] = True
            context["guardian_submitted"] = guardian
            context["registrations_submitted"] = registrations
            context["submission"] = submission

            logger.debug("  Preparing email...")
            mail_text = render_to_string("fosdem_registration/mail.txt", context)
            mail = EmailMessage(
                to=[guardian.email],
                from_email="FOSDEM Junior<junior-organisers@fosdem.org>",
                subject=f"FOSDEM JUNIOR registration {context['submission'].title}",
                body=mail_text,
            )
            mail.send()
            logger.debug(f"  Email sent to {guardian.email}")
        else:
            logger.warning("  Formset is invalid")
            logger.warning(f"  Formset errors: {formset.errors}")

        # If formset invalid, re-render page with errors
        logger.debug("  Rendering template with context")
        return render(self.request, self.template_name, context)
