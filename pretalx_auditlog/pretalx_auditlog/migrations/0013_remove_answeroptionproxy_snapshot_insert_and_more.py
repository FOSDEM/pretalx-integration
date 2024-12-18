# Generated by Django 5.1.3 on 2024-11-19 21:32

import pgtrigger.compiler
import pgtrigger.migrations
import pretalx.event.models.event
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pretalx_auditlog", "0012_alter_resourceproxyevent_link"),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name="answeroptionproxy",
            name="snapshot_insert",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="answeroptionproxy",
            name="snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="answeroptionproxy",
            name="beforedelete",
        ),
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
        pgtrigger.migrations.RemoveTrigger(
            model_name="userproxy",
            name="snapshot_insert",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="userproxy",
            name="snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="userproxy",
            name="beforedelete",
        ),
        migrations.RemoveField(
            model_name="submissionproxyevent",
            name="on_website",
        ),
        migrations.AddField(
            model_name="answeroptionproxyevent",
            name="position",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userproxyevent",
            name="avatar_thumbnail",
            field=models.ImageField(null=True, upload_to="avatars/"),
        ),
        migrations.AddField(
            model_name="userproxyevent",
            name="avatar_thumbnail_tiny",
            field=models.ImageField(null=True, upload_to="avatars/"),
        ),
        migrations.AlterField(
            model_name="eventproxyevent",
            name="header_image",
            field=models.ImageField(
                null=True, upload_to=pretalx.event.models.event.event_logo_path
            ),
        ),
        migrations.AlterField(
            model_name="eventproxyevent",
            name="logo",
            field=models.ImageField(
                null=True, upload_to=pretalx.event.models.event.event_logo_path
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="answeroptionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_answeroptionproxyevent" ("answer", "created", "id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "position", "question_id", "updated") VALUES (NEW."answer", NEW."created", NEW."id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."position", NEW."question_id", NEW."updated"); RETURN NULL;',
                    hash="faecdef085471c56e13e203804c11c6f35eaea8a",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_f4cfb",
                    table="submission_answeroption",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="answeroptionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "pretalx_auditlog_answeroptionproxyevent" ("answer", "created", "id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "position", "question_id", "updated") VALUES (NEW."answer", NEW."created", NEW."id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."position", NEW."question_id", NEW."updated"); RETURN NULL;',
                    hash="32514315ee791cab0464c0187f120b9723917909",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_e1e5b",
                    table="submission_answeroption",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="answeroptionproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_answeroptionproxyevent" ("answer", "created", "id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "position", "question_id", "updated") VALUES (OLD."answer", OLD."created", OLD."id", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."position", OLD."question_id", OLD."updated"); RETURN NULL;',
                    hash="cea967f4d6f0280ebe96b1875e71385a5fffe39e",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_6c237",
                    table="submission_answeroption",
                    when="AFTER",
                ),
            ),
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
        pgtrigger.migrations.AddTrigger(
            model_name="userproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_userproxyevent" ("avatar", "avatar_thumbnail", "avatar_thumbnail_tiny", "code", "email", "get_gravatar", "id", "is_active", "is_administrator", "is_staff", "is_superuser", "last_login", "locale", "matrix_id", "name", "nick", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "pw_reset_time", "pw_reset_token", "timezone") VALUES (NEW."avatar", NEW."avatar_thumbnail", NEW."avatar_thumbnail_tiny", NEW."code", NEW."email", NEW."get_gravatar", NEW."id", NEW."is_active", NEW."is_administrator", NEW."is_staff", NEW."is_superuser", NEW."last_login", NEW."locale", NEW."matrix_id", NEW."name", NEW."nick", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."pw_reset_time", NEW."pw_reset_token", NEW."timezone"); RETURN NULL;',
                    hash="ec59e788bfaf80b3fd6a7f7da5810684780a4954",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_7392b",
                    table="person_user",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="userproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition='WHEN (OLD."id" IS DISTINCT FROM (NEW."id") OR OLD."last_login" IS DISTINCT FROM (NEW."last_login") OR OLD."code" IS DISTINCT FROM (NEW."code") OR OLD."nick" IS DISTINCT FROM (NEW."nick") OR OLD."name" IS DISTINCT FROM (NEW."name") OR OLD."email" IS DISTINCT FROM (NEW."email") OR OLD."matrix_id" IS DISTINCT FROM (NEW."matrix_id") OR OLD."is_active" IS DISTINCT FROM (NEW."is_active") OR OLD."is_staff" IS DISTINCT FROM (NEW."is_staff") OR OLD."is_administrator" IS DISTINCT FROM (NEW."is_administrator") OR OLD."is_superuser" IS DISTINCT FROM (NEW."is_superuser") OR OLD."locale" IS DISTINCT FROM (NEW."locale") OR OLD."timezone" IS DISTINCT FROM (NEW."timezone") OR OLD."avatar" IS DISTINCT FROM (NEW."avatar") OR OLD."avatar_thumbnail" IS DISTINCT FROM (NEW."avatar_thumbnail") OR OLD."avatar_thumbnail_tiny" IS DISTINCT FROM (NEW."avatar_thumbnail_tiny") OR OLD."get_gravatar" IS DISTINCT FROM (NEW."get_gravatar") OR OLD."pw_reset_token" IS DISTINCT FROM (NEW."pw_reset_token") OR OLD."pw_reset_time" IS DISTINCT FROM (NEW."pw_reset_time"))',
                    func='INSERT INTO "pretalx_auditlog_userproxyevent" ("avatar", "avatar_thumbnail", "avatar_thumbnail_tiny", "code", "email", "get_gravatar", "id", "is_active", "is_administrator", "is_staff", "is_superuser", "last_login", "locale", "matrix_id", "name", "nick", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "pw_reset_time", "pw_reset_token", "timezone") VALUES (NEW."avatar", NEW."avatar_thumbnail", NEW."avatar_thumbnail_tiny", NEW."code", NEW."email", NEW."get_gravatar", NEW."id", NEW."is_active", NEW."is_administrator", NEW."is_staff", NEW."is_superuser", NEW."last_login", NEW."locale", NEW."matrix_id", NEW."name", NEW."nick", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."pw_reset_time", NEW."pw_reset_token", NEW."timezone"); RETURN NULL;',
                    hash="819bd15de888596da3f71a5026a30311f5ef1a23",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_f6b5c",
                    table="person_user",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="userproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_userproxyevent" ("avatar", "avatar_thumbnail", "avatar_thumbnail_tiny", "code", "email", "get_gravatar", "id", "is_active", "is_administrator", "is_staff", "is_superuser", "last_login", "locale", "matrix_id", "name", "nick", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "pw_reset_time", "pw_reset_token", "timezone") VALUES (OLD."avatar", OLD."avatar_thumbnail", OLD."avatar_thumbnail_tiny", OLD."code", OLD."email", OLD."get_gravatar", OLD."id", OLD."is_active", OLD."is_administrator", OLD."is_staff", OLD."is_superuser", OLD."last_login", OLD."locale", OLD."matrix_id", OLD."name", OLD."nick", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."pw_reset_time", OLD."pw_reset_token", OLD."timezone"); RETURN NULL;',
                    hash="d8e418f4a5102cb56265c3f58f2c41228008f2c3",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_01ad6",
                    table="person_user",
                    when="AFTER",
                ),
            ),
        ),
    ]
