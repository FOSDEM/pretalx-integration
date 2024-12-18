# Generated by Django 5.1.3 on 2024-12-03 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("devroom_settings", "0011_alter_roomsettings_control_password_and_more"),
        ("schedule", "0017_created_updated_everywhere"),
        ("submission", "0078_submission_on_website"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrackRoom",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("saturday_morning", models.BooleanField(default=False)),
                ("saturday_afternoon", models.BooleanField(default=False)),
                ("sunday_morning", models.BooleanField(default=False)),
                ("sunday_afternoon", models.BooleanField(default=False)),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="schedule.room"
                    ),
                ),
                (
                    "track",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="submission.track",
                    ),
                ),
            ],
        ),
        migrations.RunSQL(
            # Forward SQL: Migrate data from ManyToMany table to TrackRoom
            sql="""
                INSERT INTO devroom_settings_trackroom (track_id, room_id)
                SELECT track_id, room_id
                FROM devroom_settings_tracksettings_rooms dstr JOIN
                devroom_settings_tracksettings ts on dstr.id=ts.id
            """,
            # Reverse SQL: Restore data from TrackRoom back to ManyToMany table
            reverse_sql="""
                INSERT INTO devroom_settings_tracksettings_rooms (tracksettings_id, room_id)
                SELECT track_id, room_id
                FROM devroom_settings_trackroom dstr JOIN
                devroom_settings_tracksettings USING (track_id)
            """,
        ),
        migrations.RemoveField(
            model_name="tracksettings",
            name="rooms",
        ),
    ]
