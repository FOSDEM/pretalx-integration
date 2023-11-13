# Generated by Django 4.2.5 on 2023-11-09 07:54

from django.db import migrations
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pretalx_auditlog", "0001_initial"),
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
        migrations.RemoveField(
            model_name="submissionproxyevent",
            name="invitation_token",
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="submissionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (NEW."abstract", NEW."access_code_id", NEW."anonymised_data", NEW."code", NEW."content_locale", NEW."created", NEW."description", NEW."do_not_record", NEW."duration", NEW."event_id", NEW."id", NEW."image", NEW."internal_notes", NEW."is_featured", NEW."notes", NEW."pending_state", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."review_code", NEW."slot_count", NEW."state", NEW."submission_type_id", NEW."title", NEW."track_id", NEW."updated"); RETURN NULL;',
                    hash="464a0db12799077b066f4b54cbb2694974f235ae",
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
                    condition='WHEN (OLD."id" IS DISTINCT FROM (NEW."id") OR OLD."created" IS DISTINCT FROM (NEW."created") OR OLD."updated" IS DISTINCT FROM (NEW."updated") OR OLD."code" IS DISTINCT FROM (NEW."code") OR OLD."event_id" IS DISTINCT FROM (NEW."event_id") OR OLD."title" IS DISTINCT FROM (NEW."title") OR OLD."submission_type_id" IS DISTINCT FROM (NEW."submission_type_id") OR OLD."track_id" IS DISTINCT FROM (NEW."track_id") OR OLD."state" IS DISTINCT FROM (NEW."state") OR OLD."pending_state" IS DISTINCT FROM (NEW."pending_state") OR OLD."abstract" IS DISTINCT FROM (NEW."abstract") OR OLD."description" IS DISTINCT FROM (NEW."description") OR OLD."notes" IS DISTINCT FROM (NEW."notes") OR OLD."internal_notes" IS DISTINCT FROM (NEW."internal_notes") OR OLD."duration" IS DISTINCT FROM (NEW."duration") OR OLD."slot_count" IS DISTINCT FROM (NEW."slot_count") OR OLD."content_locale" IS DISTINCT FROM (NEW."content_locale") OR OLD."is_featured" IS DISTINCT FROM (NEW."is_featured") OR OLD."do_not_record" IS DISTINCT FROM (NEW."do_not_record") OR OLD."image" IS DISTINCT FROM (NEW."image") OR OLD."access_code_id" IS DISTINCT FROM (NEW."access_code_id") OR OLD."review_code" IS DISTINCT FROM (NEW."review_code") OR OLD."anonymised_data" IS DISTINCT FROM (NEW."anonymised_data"))',
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (NEW."abstract", NEW."access_code_id", NEW."anonymised_data", NEW."code", NEW."content_locale", NEW."created", NEW."description", NEW."do_not_record", NEW."duration", NEW."event_id", NEW."id", NEW."image", NEW."internal_notes", NEW."is_featured", NEW."notes", NEW."pending_state", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."review_code", NEW."slot_count", NEW."state", NEW."submission_type_id", NEW."title", NEW."track_id", NEW."updated"); RETURN NULL;',
                    hash="bdcc551c13aff874e3b40cf51b6c45150d1bb4cf",
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
                    func='INSERT INTO "pretalx_auditlog_submissionproxyevent" ("abstract", "access_code_id", "anonymised_data", "code", "content_locale", "created", "description", "do_not_record", "duration", "event_id", "id", "image", "internal_notes", "is_featured", "notes", "pending_state", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "review_code", "slot_count", "state", "submission_type_id", "title", "track_id", "updated") VALUES (OLD."abstract", OLD."access_code_id", OLD."anonymised_data", OLD."code", OLD."content_locale", OLD."created", OLD."description", OLD."do_not_record", OLD."duration", OLD."event_id", OLD."id", OLD."image", OLD."internal_notes", OLD."is_featured", OLD."notes", OLD."pending_state", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."review_code", OLD."slot_count", OLD."state", OLD."submission_type_id", OLD."title", OLD."track_id", OLD."updated"); RETURN NULL;',
                    hash="d8fb8d299ba64e1c0aeb18a5d647ffdc5c50f681",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_c739f",
                    table="submission_submission",
                    when="AFTER",
                ),
            ),
        ),
    ]