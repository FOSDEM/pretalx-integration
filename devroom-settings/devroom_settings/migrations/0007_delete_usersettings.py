# Generated by Django 4.2.5 on 2024-01-06 02:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("devroom_settings", "0006_remove_usersettings_visible_usersettings_matrix_id"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UserSettings",
        ),
    ]
