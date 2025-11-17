from django.db.models import Count, F, IntegerField, OuterRef, Subquery
from django.views.generic import ListView
from pretalx.common.views.mixins import PermissionRequired
from pretalx.submission.models import Submission
from pretalx.submission.models.question import Answer

from fosdem_registration.models import FosdemRegistration, FosdemRegistrationTrack


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
            Submission.objects.filter(track__fosdemregistrationtrack__isnull=False)
            .annotate(
                nr_registrations=Count("fosdemregistration"),
                max_number=Subquery(max_participants_subquery),
            )
            .select_related("track")
            .order_by("track__name", "title")
        )
        return submissions


from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import FosdemRegistrationForm
from .models import FosdemRegistration


class RegisterPersonView(FormView):
    template_name = "fosdem_registration/register.html"
    form_class = FosdemRegistrationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["session"] = Submission.objects.get(code=self.kwargs["submission_code"])
        return kwargs

    def get_success_url(self):
        # Redirect back to the same form with a flag
        return (
            reverse(
                "register_person",
                kwargs={"submission_code": self.kwargs["submission_code"]},
            )
            + "?added=1"
        )

    def form_valid(self, form):
        registration = form.save(commit=False)
        registration.session = Submission.objects.get(
            code=self.kwargs["submission_code"]
        )
        registration.registering_person = self.request.user
        registration.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["added"] = self.request.GET.get("added") == "1"
        return context
