from pretalx.schedule.exporters import FrabJsonExporter


class FosdemJsonExporter(FrabJsonExporter):
    identifier = "schedule_fosdem.json"
    verbose_name = "FOSDEM JSON export"
    public = True
    Icon = "fa-solid fa-file-json"
    cors = "*"

    def get_data(self, **kwargs):
        data = super().get_data(**kwargs)
        data["conference"]["fringe"] = self.fringe()
        data["conference"]["tracks"] = self.tracks()
        return data

    def tracks(self):
        tracks = [
            {
                "name": str(track.name),
                "slug": track.slug,
                "color": track.color,
                "type": track.tracksettings.get_track_type_display(),
            }
            for track in self.event.tracks.select_related("tracksettings").all()
        ]
        return tracks

    def fringe(self):
        try:
            from pretalx_fringe.models import FringeActivity
        except ImportError:
            return []
        activities = FringeActivity.objects.filter(
            event=self.event, online=FringeActivity.TRUE
        )
        activities = activities.values(
            "url",
            "location",
            "starts",
            "ends",
            "cost",
            "registration",
            "contact",
            "name",
        )
        return activities
