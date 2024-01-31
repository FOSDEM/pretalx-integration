from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils.formats import get_format
from django.utils.timezone import override as tzoverride
from django.utils.translation import override
from django_scopes import scope
from pretalx.common.context_processors import get_day_month_date_format
from pretalx.event.models import Event
from pretalx.mail.models import QueuedMail


class Command(BaseCommand):
    help = "Bulk send mails for speaker to outbox"

    def add_arguments(self, parser):
        parser.add_argument("event", help="Event slug")

    def handle(self, *args, **kwargs):
        event_slug = kwargs["event"]
        event = Event.objects.get(slug=event_slug)
        send_speaker_mails(event)


def send_speaker_mails(event, save=True):
    """A list of unsaved :class:`~pretalx.mail.models.QueuedMail` objects
    to be sent to all speakers"""
    mails = []
    date_formats = {}

    with scope(event=event):
        speakers = list(event.speakers.all())[0:1] # limiting to one for tests

    for speaker in speakers:
        locale = speaker.locale if speaker.locale in event.locales else event.locale
        with override(locale), tzoverride(event.tz):
            date_format = date_formats.get(locale)
            if not date_format:
                date_format = (
                    get_day_month_date_format() + ", " + get_format("TIME_FORMAT")
                )
                date_formats[locale] = date_format
        with scope(event=event):
            slots = event.wip_schedule.scheduled_talks.filter(
                submission__speakers=speaker
            )

        # generate fosdem website links from slots
        website_links = ["https://fosdem.org/2024/schedule/event/"+ slot.frab_slug for slot in slots]

        mail = QueuedMail(
            event=event,
            subject="Speaker Instructions for FOSDEM (test)",
            # to=speaker.email,
            text=get_template("speaker_mail.html").render(
                context={"slots": slots, "links": website_links}
            ),
            locale=locale,
        )
        mail.save()
        mail.to_users.set([speaker])
