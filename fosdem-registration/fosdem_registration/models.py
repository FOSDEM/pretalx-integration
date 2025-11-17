from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# stores for which tracks registration is required
class FosdemRegistrationTrack(models.Model):
    track = models.OneToOneField(to="submission.Track", on_delete=models.CASCADE)
    # answer that contains max number of participants
    max_number_question = models.ForeignKey(
        to="submission.Question", on_delete=models.CASCADE
    )
    # teams that can access registrations
    teams = models.ManyToManyField(to="event.Team")


class FosdemRegistration(models.Model):
    session = models.ForeignKey(to="submission.submission", on_delete=models.CASCADE)
    registering_person = models.ForeignKey(to="person.User", on_delete=models.CASCADE)
    nickname = models.CharField()
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="age in years of kid on the day of the session",
    )

    def clean(self):
        """Prevent creating a registration if the track is full."""
        # Get the track for the session
        track = getattr(self.session, "track", None)
        if not track:
            return

        reg_track = FosdemRegistrationTrack.objects.get(track=track)

        current_count = FosdemRegistration.objects.filter(session__track=track).count()
        max_number = int(
            self.session.answers.get(question=reg_track.max_number_question).answer
        )
        if current_count >= max_number:
            raise ValidationError(
                f"Registration limit ({reg_track.max_number}) reached for {track}."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
