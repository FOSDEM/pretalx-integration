from django.db.models import Count, IntegerField, OuterRef, Subquery
from submission.models import Submission
from yourapp.models import FosdemRegistration, FosdemRegistrationTrack


def registration_overview(request):
    max_number_subquery = FosdemRegistrationTrack.objects.filter(
        track=OuterRef("track")
    ).values("max_number_answer__response")[:1]

    submissions = (
        Submission.objects.filter(track__fosdemregistrationtrack__isnull=False)
        .annotate(
            nr_registrations=Count("fosdemregistration"),
            max_number=Subquery(max_number_subquery, output_field=IntegerField()),
        )
        .select_related("track")
        .order_by("track__name", "title")
    )

    return render(
        request, "fosdem/registration_overview.html", {"submissions": submissions}
    )
