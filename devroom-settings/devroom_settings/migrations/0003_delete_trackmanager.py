# Generated by Django 4.2.5 on 2023-11-15 16:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("devroom_settings", "0002_tracksettings_manager_team_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TrackManager",
        ),
    ]
