# Generated by Django 4.2.5 on 2023-11-05 23:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("submission", "0074_created_updated_everywhere"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrackSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("slug", models.SlugField(max_length=63)),
                ("mail", models.EmailField(max_length=254)),
                ("cfp_url", models.CharField(max_length=254, null=True)),
                ("online_qa", models.BooleanField(default=False)),
                (
                    "track",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="submission.track",
                    ),
                ),
            ],
        ),
    ]
