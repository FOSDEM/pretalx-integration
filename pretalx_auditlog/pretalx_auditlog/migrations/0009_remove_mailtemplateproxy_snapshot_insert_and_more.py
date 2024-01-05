# Generated by Django 4.2.5 on 2023-12-29 13:33

from django.db import migrations, models
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "pretalx_auditlog",
            "0008_activitylogproxy_answeroptionproxy_cfpproxy_and_more",
        ),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name="mailtemplateproxy",
            name="snapshot_insert",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="mailtemplateproxy",
            name="snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="mailtemplateproxy",
            name="beforedelete",
        ),
        migrations.AddField(
            model_name="mailtemplateproxyevent",
            name="cc",
            field=models.CharField(max_length=1000, null=True),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="mailtemplateproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_mailtemplateproxyevent" ("bcc", "cc", "created", "event_id", "id", "is_auto_created", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "reply_to", "subject", "text", "updated") VALUES (NEW."bcc", NEW."cc", NEW."created", NEW."event_id", NEW."id", NEW."is_auto_created", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."reply_to", NEW."subject", NEW."text", NEW."updated"); RETURN NULL;',
                    hash="297f2ebcddc081205c48df6868209ed37b2fb565",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_b1d9d",
                    table="mail_mailtemplate",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="mailtemplateproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "pretalx_auditlog_mailtemplateproxyevent" ("bcc", "cc", "created", "event_id", "id", "is_auto_created", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "reply_to", "subject", "text", "updated") VALUES (NEW."bcc", NEW."cc", NEW."created", NEW."event_id", NEW."id", NEW."is_auto_created", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."reply_to", NEW."subject", NEW."text", NEW."updated"); RETURN NULL;',
                    hash="e2b86d6babd77cfa5dad007e9649d7e977d9e7c9",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_b51f6",
                    table="mail_mailtemplate",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="mailtemplateproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_mailtemplateproxyevent" ("bcc", "cc", "created", "event_id", "id", "is_auto_created", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "reply_to", "subject", "text", "updated") VALUES (OLD."bcc", OLD."cc", OLD."created", OLD."event_id", OLD."id", OLD."is_auto_created", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."reply_to", OLD."subject", OLD."text", OLD."updated"); RETURN NULL;',
                    hash="4a67a6d7d708f2728fdb77e4645c33bcd7cac251",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_cd1da",
                    table="mail_mailtemplate",
                    when="AFTER",
                ),
            ),
        ),
    ]
