# Generated by Django 5.1.3 on 2024-11-20 20:07

import pgtrigger.compiler
import pgtrigger.migrations
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pretalx_auditlog", "0013_remove_answeroptionproxy_snapshot_insert_and_more"),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name="submissionproxy",
            name="snapshot_insert",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="submissionproxy",
            name="snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="submissionproxy",
            name="beforedelete",
        ),
        migrations.AddField(
            model_name="submissionproxyevent",
            name="on_website",
            field=models.BooleanField(default=True),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="submissionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "on_website", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (NEW."abstract", NEW."access_code_id", NEW."anonymised_data", NEW."code", NEW."content_locale", NEW."created", NEW."description", NEW."do_not_record", NEW."duration", NEW."event_id", NEW."id", NEW."image", NEW."internal_notes", NEW."is_featured", NEW."notes", NEW."on_website", NEW."pending_state", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."review_code", NEW."slot_count", NEW."state", NEW."submission_type_id", NEW."title", NEW."track_id", NEW."updated"); RETURN NULL;',
                    hash="1c855333ba4ad8ccaac66fb2dc63bda97545aec3",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_505a6",
                    table="submission_submission",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="submissionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition='WHEN (OLD."id" IS DISTINCT FROM (NEW."id") OR OLD."created" IS DISTINCT FROM (NEW."created") OR OLD."updated" IS DISTINCT FROM (NEW."updated") OR OLD."code" IS DISTINCT FROM (NEW."code") OR OLD."event_id" IS DISTINCT FROM (NEW."event_id") OR OLD."title" IS DISTINCT FROM (NEW."title") OR OLD."submission_type_id" IS DISTINCT FROM (NEW."submission_type_id") OR OLD."track_id" IS DISTINCT FROM (NEW."track_id") OR OLD."state" IS DISTINCT FROM (NEW."state") OR OLD."pending_state" IS DISTINCT FROM (NEW."pending_state") OR OLD."abstract" IS DISTINCT FROM (NEW."abstract") OR OLD."description" IS DISTINCT FROM (NEW."description") OR OLD."notes" IS DISTINCT FROM (NEW."notes") OR OLD."internal_notes" IS DISTINCT FROM (NEW."internal_notes") OR OLD."duration" IS DISTINCT FROM (NEW."duration") OR OLD."slot_count" IS DISTINCT FROM (NEW."slot_count") OR OLD."content_locale" IS DISTINCT FROM (NEW."content_locale") OR OLD."is_featured" IS DISTINCT FROM (NEW."is_featured") OR OLD."do_not_record" IS DISTINCT FROM (NEW."do_not_record") OR OLD."image" IS DISTINCT FROM (NEW."image") OR OLD."access_code_id" IS DISTINCT FROM (NEW."access_code_id") OR OLD."review_code" IS DISTINCT FROM (NEW."review_code") OR OLD."anonymised_data" IS DISTINCT FROM (NEW."anonymised_data") OR OLD."on_website" IS DISTINCT FROM (NEW."on_website"))',
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "on_website", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (NEW."abstract", NEW."access_code_id", NEW."anonymised_data", NEW."code", NEW."content_locale", NEW."created", NEW."description", NEW."do_not_record", NEW."duration", NEW."event_id", NEW."id", NEW."image", NEW."internal_notes", NEW."is_featured", NEW."notes", NEW."on_website", NEW."pending_state", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."review_code", NEW."slot_count", NEW."state", NEW."submission_type_id", NEW."title", NEW."track_id", NEW."updated"); RETURN NULL;',
                    hash="b257514049eed8c05ba334828ad46ee96f59bc06",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_49420",
                    table="submission_submission",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="submissionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "on_website", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (OLD."abstract", OLD."access_code_id", OLD."anonymised_data", OLD."code", OLD."content_locale", OLD."created", OLD."description", OLD."do_not_record", OLD."duration", OLD."event_id", OLD."id", OLD."image", OLD."internal_notes", OLD."is_featured", OLD."notes", OLD."on_website", OLD."pending_state", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."review_code", OLD."slot_count", OLD."state", OLD."submission_type_id", OLD."title", OLD."track_id", OLD."updated"); RETURN NULL;',
                    hash="426940dec027fe8fc42e9feafb03827229af2602",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_c739f",
                    table="submission_submission",
                    when="AFTER",
                ),
            ),
        ),
    ]
