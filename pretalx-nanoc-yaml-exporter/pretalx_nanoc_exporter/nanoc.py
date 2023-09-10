from pathlib import Path
import datetime
from collections import defaultdict

import pytz
import yaml
from django.db.models import Prefetch
from django.template.loader import get_template
from django.utils.functional import cached_property
from pretalx.common.exporter import BaseExporter
from pretalx.common.urls import get_base_url
from pretalx.schedule.exporters import ScheduleData
from pretalx.schedule.models import Room, TalkSlot
from pretalx.submission.models import Submission, Track

tz=pytz.timezone("Europe/Brussels")

def represent_time(dumper, data):
    # return dumper.represent_scalar('tag:yaml.org,2002:timestamp', data.strftime('%H:%M:%S'))
    return dumper.represent_scalar("timestamp", data.strftime("%H:%M"))


def represent_timedelta(dumper, data):
    seconds = data.total_seconds()
    hours = int(seconds // 3600)
    minutes = int(seconds // 60 - 60 * hours)
    return dumper.represent_scalar("timedelta", f"{hours:02d}:{minutes:02d}:00")

def represent_datetime(dumper, data):
    """Make sure that timezone is added"""
    return dumper.represent_scalar("timestamp", str(data.astimezone(tz)))


# Register the custom representer for datetime.time
yaml.add_representer(datetime.time, represent_time)
yaml.add_representer(datetime.timedelta, represent_timedelta)
yaml.add_representer(datetime.datetime, represent_datetime)

from yaml.representer import Representer

yaml.add_representer(defaultdict, Representer.represent_dict)


def time_to_index(timevalue):
    return int((timevalue.hour * 60 + timevalue.minute) // 5)


class NanocExporter(ScheduleData):
    identifier = "NanocExporter"
    verbose_name = "Exports to nanoc for FOSDEM website"
    show_qrcode = False
    public = True  # easier for testing
    icon = "fa-microchip"
    group = "submission"

    @cached_property
    def rooms(self):
        """
        demo:

        rooms:
          janson:
            conference_room: Janson
            size: 145
            rank: 10
            slug: janson
            title: Janson
            chat_link: xxx
            events:
            - aa
            - bb
            events_by_day:
            - aa
            - bb

        """
        schedule = self.schedule
        rooms = Room.objects.prefetch_related(
            Prefetch(
                "talks",
                queryset=TalkSlot.objects.filter(
                    schedule=schedule, is_visible=True
                ).select_related("submission"),
                to_attr="talks_current",
            )
        )

        events_by_day = {}
        start_time = {}
        end_time = {}
        start_time_index = {}
        end_time_index = {}

        for room in rooms:
            room_slug = str(room.name).lower()
            events_by_day[room.pk] = {day: [] for day in self.days}
            start_time[room_slug] = {}
            end_time[room_slug] = {}
            start_time_index[room_slug] = {}
            end_time_index[room_slug] = {}
            for talk in room.talks_current:
                day = talk.start.strftime("%A").lower()
                events_by_day[room.pk][day].append(talk.frab_slug)
                if day in start_time[room_slug]:
                    start_time[room_slug][day] = min(
                        talk.start.time(), start_time[room_slug][day]
                    )
                    end_time[room_slug][day] = max(
                        talk.end.time(), end_time[room_slug][day]
                    )
                else:
                    start_time[room_slug][day] = talk.start.astimezone(tz).time()
                    end_time[room_slug][day] = talk.end.astimezone(tz).time()
            for day in start_time_index[room_slug]:
                start_time_index[room_slug][day] = time_to_index(
                    start_time[room_slug][day]
                )
                end_time_index[room_slug][day] = time_to_index(end_time[room_slug][day])
        rooms = {
            str(room.name).lower(): {
                "conference_room_id": room.pk,
                "conference_room": str(room.name),
                "size": room.capacity,
                "rank": room.position,
                "slug": str(room.name).lower(),
                "chat_link": "https://chat.fosdem.org/todo",
                "live_video_link": f"https://live.fosdem.org/watch/{str(room.name)}",
                "title": str(room.name),
                "events": [talk.frab_slug for talk in room.talks_current],
                "events_by_day": events_by_day[room.pk],
                "start_time": start_time[str(room.name).lower()],
                "end_time": end_time[str(room.name).lower()],
                "start_time_index": start_time_index[str(room.name).lower()],
                "end_time_index": end_time_index[str(room.name).lower()],
            }
            for room in rooms
        }
        return rooms

    @cached_property
    def tracks(self):
        tracks = Track.objects.filter(event=self.event)
        tracks_dict = {}
        for track in tracks:
            track_talks_day = {day: [] for day in self.days}

            talk_slots = TalkSlot.objects.filter(
                submission__track=track, schedule=self.schedule, is_visible=True
            )
            start_time = {}
            end_time = {}
            start_time_index = {}
            end_time_index = {}
            track_talks = [slot.frab_slug for slot in talk_slots]
            track_rooms = []
            events_per_room_per_day = {day: defaultdict(list) for day in self.days}

            for slot in talk_slots:
                room = str(slot.room.name).lower()
                day = slot.start.strftime("%A").lower()
                track_talks_day[day].append(slot.frab_slug)
                if room not in track_rooms:
                    track_rooms.append(room)
                events_per_room_per_day[day][room].append(slot.frab_slug)

                if day in start_time:
                    start_time[day] = min(slot.start.time(), start_time[day])
                    end_time[day] = max(slot.end.time(), end_time[day])
                else:
                    start_time[day] = slot.start.time()
                    end_time[day] = slot.end.time()
            for day in start_time:
                start_time_index[day] = time_to_index(start_time[day])
                end_time_index[day] = time_to_index(end_time[day])
            tracks_dict[track.slug] = {
                "conference_track": str(track.name),
                "name": str(track.name),
                "title": str(track.name),
                "conference_track_id": track.pk,
                "conference_call_for_papers_url": "",  # TODO?
                "slug": track.slug,
                "rank": track.pk,  # TODO - cfr https://github.com/pretalx/pretalx/issues/1305
                "type": "maintrack",  # TODO - either include in pretalx upstream/plugin or keep in exporter?
                "rooms": track_rooms,
                "events": track_talks,
                "events_by_day": track_talks_day,
                "events_per_room_per_day": events_per_room_per_day,
                "start_time": start_time,
                "end_time": end_time,
                "start_time_index": start_time_index,
                "end_time_index": end_time_index,
            }
        return tracks_dict

    @cached_property
    def talks(self):
        talks = {}
        for day in self.data:
            for room in day["rooms"]:
                for talk in room["talks"]:
                    track = talk.submission.track
                    day_string = talk.start.strftime("%A")
                    links = [{"title": resource.description, "url": resource.link} for resource in talk.submission.resources.filter(link__isnull=False)]
                    attachments = [{"title": resource.description, 
                                    "file": "/media-static/" + resource.resource.name,
                                    "filename": Path(resource.resource.name).name,
                                    "identifier": "/media-static/" + resource.resource.name,
                                    "type": "slides", # TODO - or not -influences link+icon
                                    "size": resource.resource.size,
                                    "mime": "image/png", # TODO: is this actually used? we could use "magic" for this
                                    "id": resource.pk,
                                    "event_id": talk.pk,
                                    "event_slug": talk.frab_slug
                                    } for resource in talk.submission.resources.exclude(resource="")]
                    talks[talk.frab_slug] = {
                        "event_id": talk.pk,
                        "conference_track_id": track.pk,
                        "title": talk.submission.title,
                        "subtitle": "",  # this does not exist in pretalx
                        "slug": talk.frab_slug,
                        "subtitle": "",
                        "abstract": talk.submission.abstract,
                        "description": str(talk.submission.description),
                        "start_time": talk.start.astimezone(tz).time(),
                        "end_time": talk.end.astimezone(tz).time(),
                        "start_datetime": talk.start,
                        "end_datetime": talk.end,
                        "start_time_index": time_to_index(talk.start.time()),
                        "end_time_index": time_to_index(talk.end.time()),
                        "duration": talk.end - talk.start,
                        "day": day_string.lower(),
                        "day_name": day_string,
                        "conference_day_id": talk.start.weekday(),
                        "speakers": [
                            speaker.code for speaker in talk.submission.speakers.all()
                        ],
                        "track": track.slug,
                        "track_name": str(track.name),
                        "track_full_name": str(track.name),
                        "type": "maintrack",  # TODO
                        "room": str(talk.room.name).lower(),
                        "room_name": str(talk.room.name),
                        "room_rank": talk.room.position,
                        "conference_room_id": talk.room.pk,
                        "language": "en",
                        "attachments": attachments,
                        "links": links
                        # logo TODO
                    }
        return talks

    @cached_property
    def days(self):
        tz = pytz.timezone(self.event.timezone)
        days = {}
        for day in self.data:
            day_slug = day["start"].strftime("%A").lower()

            # TODO FIXED for now as day["start"] is 00
            # and day["end"] will end up being before day["start"]
            #start_time = day["start"].astimezone(tz).time()
            #end_time = (day["start"].astimezone(tz) + datetime.timedelta(hours=10)).time()

            start_time = datetime.time(hour=9)
            end_time = datetime.time(hour=17)
            days[day_slug] = {
                "conference_day_id": day["start"].weekday(),
                "name": day["start"].strftime("%A"),
                "slug": day["start"].strftime("%A").lower(),
                "title": day["start"].strftime("%A"),
                "conference_day": day["start"].date(),
                "start_time": start_time,
                # "end_time": day["end"].time() - will not work - next day!
                "end_time": end_time,
                "start_time_index": time_to_index(start_time),
                "end_time_index": time_to_index(end_time),
            }
        return days

    @cached_property
    def speakers(self):
        # speakers = talk_slot.submission.speakers.all()
        speakers_dict = {}
        for day in self.data:
            for room in day["rooms"]:
                for talk in room["talks"]:
                    for speaker in talk.submission.speakers.all():
                        if speaker.code not in speakers_dict:
                            speakers_dict[speaker.code] = {
                                "person_id": speaker.pk,  # TODO: check if this is actually used
                                "title": speaker.name,
                                "public_name": speaker.name,
                                "first_name": "",
                                "last_name": "",
                                "nickname": "",
                                "name": speaker.name,
                                "slug": speaker.code,
                                "gender": "",  # check whether we need/want this
                                "sortname": speaker.name.upper(),
                                "abstract": speaker.profiles.get(event=self.event).biography,
                                "description": "",  # TODO: do we use this anywhere where abstract is not shown? Pretalx does not have two fields
                                "conference_person_id": speaker.pk,  # not equal to person_id in penta
                                "links": [],
                                "events": [talk.frab_slug],
                                # "events_by_day:": events_by_day
                            }
                        else:
                            speakers_dict[speaker.code]["events"].append(talk.frab_slug)

        return speakers_dict

    def render(self):
        context = {
            "data": self.data,
            "metadata": self.metadata,
            "schedule": self.schedule,
            "event": self.event,
            "version": "0.0.1",
            "base_url": get_base_url(self.event),
            "rooms": self.rooms,
        }
        conference = {
            "conference_id": self.event.pk,
            "acronym": self.event.slug,
            "title": str(self.event.name),
            "subtitle": "TODO- nanoc export test",
            "conference_phase": "confusion",
            "venue": "ULB (Université Libre de Bruxelles)",
            "city": "Brussels",
            "country": "be",
            "timezone": "Europe/Brussels",
            "currency": "EUR",
            "timeslot_duration": datetime.timedelta(hours=0, minutes=5),
            "default_timeslots": 10,
            "max_timeslot_duration": 25,
            "day_change": datetime.time(0, 0),  # TODO: might need time encoding
            "remark": "",
            "homepage": "https://fosdem.org/",
            "abstract_length": "",
            "description_length": "",
            "export_base_url": "https://fosdem.org/2024/schedule",
            "schedule_html_include": "",
            "feedback_base_url": "https://fosdem.org/TODO",
            "css": "",
            "email": "info@fosdem.org",
            "f_feedback_enabled": False,
            "f_submission_enabled": False,
            "f_submission_new_events": False,
            "f_submission_writable": False,
            "f_visitor_enabled": False,
            "f_reconfirmation_enabled": False,
            "f_travel_enabled": False,
            "f_matrix_bot_enabled": False,
            "f_timeshift_test_enabled": False,
            "timeshift_offset": datetime.time(0, 0),
            "test_conference_room_id": "",
            "timeshift_offset_minutes": "",
        }

        content = {
            "conference": conference,
            "days": self.days,
            "rooms": self.rooms,
            "tracks": self.tracks,
            "events": self.talks,
            "speakers": self.speakers,
        }
        dumped_yaml = yaml.dump(
            content, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        # remove timestamp pointers to make sure we have plain strings
        dumped_yaml = dumped_yaml.replace("!<timestamp> ", "").replace(
            "!<timedelta> ", ""
        )
        return "nanoc.yaml", "application/yaml", dumped_yaml

    # def urls(self):
    #     return ["nanoc.yaml"]
