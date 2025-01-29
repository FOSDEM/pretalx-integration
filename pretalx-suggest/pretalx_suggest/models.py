from django.db import models
from pretalx.person.models.user import User


class TalkSuggestion(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, help_text="Name of the speaker/project"
    )

    why = models.TextField(
        verbose_name="Why do you recommend this speaker?",
        help_text="Why do you recommend this speaker? Please include links to relevant open source code (if applicable), recording of previous talks, ...",
    )

    speaker_connection = models.TextField(
        help_text="What is your connection to the speaker (if any). Would you like to help us contact this person?"
    )
    contact = models.EmailField(
        help_text="Email address of the speaker (if you have this)",
        null=True,
        blank=True,
    )
    other = models.TextField(
        verbose_name="Other contact information",
        help_text="Other relevant information to contact the speaker.",
    )

    internal_notes = models.TextField(help_text="Internal notes for FOSDEM staff")

    submitter = models.ForeignKey(to=User, on_delete=models.CASCADE)
    sort_order = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set sort_order to id * 10 if not defined
        if self.sort_order is None:
            if self.id is None:
                super().save(*args, **kwargs)
            self.sort_order = self.id * 10
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["sort_order"]
