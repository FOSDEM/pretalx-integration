from django.core.exceptions import ValidationError
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


class FosdemRegistrationGuardian(models.Model):
    name = models.CharField(max_length=200, help_text="Name of parent or guardian")
    email = models.EmailField(
        help_text="Email address of parent or guardian. Registration confirmation will be sent here"
    )
    contact_number = models.CharField(
        max_length=20, help_text="Emergency phone number of parent or guardian"
    )


class FosdemRegistration(models.Model):
    session = models.ForeignKey(to="submission.submission", on_delete=models.CASCADE)
    registering_person = models.ForeignKey(
        to=FosdemRegistrationGuardian, on_delete=models.CASCADE
    )
    nickname = models.CharField(max_length=100, help_text="child name or nickname")
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="age in years of child on the day of the session",
    )
    special_needs = models.CharField(max_length=400, blank=True)
    removed = models.BooleanField(default=False, help_text="registration removed")

    def clean(self):
        """Prevent creating a registration if the track is full."""
        # Get the track for the session
        track = getattr(self.session, "track", None)
        if not track:
            return

        reg_track = FosdemRegistrationTrack.objects.get(track=track)

        current_count = FosdemRegistration.objects.filter(
            session=self.session, removed=False
        ).count()
        max_number = int(
            self.session.answers.get(question=reg_track.max_number_question).answer
        )
        print(f"current_count: {current_count}; max_number: {max_number}")
        if current_count >= max_number:
            print("max reached")
            raise ValidationError(
                f"Registration limit ({reg_track.max_number_question}) reached for {track}."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
