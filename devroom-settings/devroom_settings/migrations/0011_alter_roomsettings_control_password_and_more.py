# Generated by Django 4.2.5 on 2024-10-28 22:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("devroom_settings", "0010_roomsettings_control_password"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roomsettings",
            name="control_password",
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="tracksettings",
            name="track_type",
            field=models.CharField(max_length=50),
        ),
    ]