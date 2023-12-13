# Generated by Django 4.2.5 on 2023-11-23 00:09

from django.db import migrations, models
import django.db.models.deletion
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):
    dependencies = [
        ("person", "0027_created_updated_everywhere"),
        ("pghistory", "0005_events_middlewareevents"),
        ("schedule", "0017_created_updated_everywhere"),
        ("event", "0035_created_updated_everywhere"),
        ("pretalx_auditlog", "0004_remove_teaminviteproxy_snapshot_insert_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvailabilityProxy",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("schedule.availability",),
        ),
        migrations.CreateModel(
            name="AvailabilityProxyEvent",
            fields=[
                ("pgh_id", models.AutoField(primary_key=True, serialize=False)),
                ("pgh_created_at", models.DateTimeField(auto_now_add=True)),
                ("pgh_label", models.TextField()),
                ("id", models.IntegerField()),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated", models.DateTimeField(auto_now=True, null=True)),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField()),
                (
                    "event",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        related_query_name="+",
                        to="event.event",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        related_query_name="+",
                        to="person.speakerprofile",
                    ),
                ),
                (
                    "pgh_context",
                    models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="pghistory.context",
                    ),
                ),
                (
                    "pgh_obj",
                    models.ForeignKey(
                        db_constraint=False,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="log_events",
                        related_query_name="log_events",
                        to="pretalx_auditlog.availabilityproxy",
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        related_query_name="+",
                        to="schedule.room",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="availabilityproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_availabilityproxyevent" ("created", "end", "event_id", "id", "person_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "room_id", "start", "updated") VALUES (NEW."created", NEW."end", NEW."event_id", NEW."id", NEW."person_id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."room_id", NEW."start", NEW."updated"); RETURN NULL;',
                    hash="389b58db9e700855f6f93b0af8114f374f719e28",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_fd4fc",
                    table="schedule_availability",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="availabilityproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "pretalx_auditlog_availabilityproxyevent" ("created", "end", "event_id", "id", "person_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "room_id", "start", "updated") VALUES (NEW."created", NEW."end", NEW."event_id", NEW."id", NEW."person_id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."room_id", NEW."start", NEW."updated"); RETURN NULL;',
                    hash="de4d6e73f47227586432f27a743f2fb9d5869257",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_601c3",
                    table="schedule_availability",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="availabilityproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_availabilityproxyevent" ("created", "end", "event_id", "id", "person_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "room_id", "start", "updated") VALUES (OLD."created", OLD."end", OLD."event_id", OLD."id", OLD."person_id", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."room_id", OLD."start", OLD."updated"); RETURN NULL;',
                    hash="4bee2b051bcc68f3e7f846fba941c5baf2e2c5b0",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_22adb",
                    table="schedule_availability",
                    when="AFTER",
                ),
            ),
        ),
    ]