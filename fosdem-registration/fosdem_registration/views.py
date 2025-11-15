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
