# Generated by Django 4.2.5 on 2023-11-15 16:35

import pgtrigger.compiler
import pgtrigger.migrations
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pretalx_auditlog", "0002_remove_submissionproxy_snapshot_insert_and_more"),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name="eventproxy",
            name="snapshot_insert",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="eventproxy",
            name="snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="eventproxy",
            name="beforedelete",
        ),
        migrations.RemoveField(
            model_name="eventproxyevent",
            name="updated",
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="eventproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_insert",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_eventproxyevent" ("accept_template_id", "ack_template_id", "content_locale_array", "created", "custom_css", "custom_domain", "date_from", "date_to", "display_settings", "email", "feature_flags", "featured_sessions_text", "header_image", "id", "is_public", "landing_page_text", "locale", "locale_array", "logo", "mail_settings", "name", "organiser_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "plugins", "primary_color", "question_template_id", "reject_template_id", "review_settings", "slug", "timezone", "update_template_id") VALUES (NEW."accept_template_id", NEW."ack_template_id", NEW."content_locale_array", NEW."created", NEW."custom_css", NEW."custom_domain", NEW."date_from", NEW."date_to", NEW."display_settings", NEW."email", NEW."feature_flags", NEW."featured_sessions_text", NEW."header_image", NEW."id", NEW."is_public", NEW."landing_page_text", NEW."locale", NEW."locale_array", NEW."logo", NEW."mail_settings", NEW."name", NEW."organiser_id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."plugins", NEW."primary_color", NEW."question_template_id", NEW."reject_template_id", NEW."review_settings", NEW."slug", NEW."timezone", NEW."update_template_id"); RETURN NULL;',
                    hash="996e3f05a7d17aa8c59fa4ca7151485cf3b70b5d",
                    operation="INSERT",
                    pgid="pgtrigger_snapshot_insert_adba0",
                    table="event_event",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="eventproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition='WHEN (OLD."id" IS DISTINCT FROM (NEW."id") OR OLD."created" IS DISTINCT FROM (NEW."created") OR OLD."name" IS DISTINCT FROM (NEW."name") OR OLD."slug" IS DISTINCT FROM (NEW."slug") OR OLD."organiser_id" IS DISTINCT FROM (NEW."organiser_id") OR OLD."is_public" IS DISTINCT FROM (NEW."is_public") OR OLD."date_from" IS DISTINCT FROM (NEW."date_from") OR OLD."date_to" IS DISTINCT FROM (NEW."date_to") OR OLD."timezone" IS DISTINCT FROM (NEW."timezone") OR OLD."email" IS DISTINCT FROM (NEW."email") OR OLD."custom_domain" IS DISTINCT FROM (NEW."custom_domain") OR OLD."feature_flags" IS DISTINCT FROM (NEW."feature_flags") OR OLD."display_settings" IS DISTINCT FROM (NEW."display_settings") OR OLD."review_settings" IS DISTINCT FROM (NEW."review_settings") OR OLD."mail_settings" IS DISTINCT FROM (NEW."mail_settings") OR OLD."primary_color" IS DISTINCT FROM (NEW."primary_color") OR OLD."custom_css" IS DISTINCT FROM (NEW."custom_css") OR OLD."logo" IS DISTINCT FROM (NEW."logo") OR OLD."header_image" IS DISTINCT FROM (NEW."header_image") OR OLD."locale_array" IS DISTINCT FROM (NEW."locale_array") OR OLD."content_locale_array" IS DISTINCT FROM (NEW."content_locale_array") OR OLD."locale" IS DISTINCT FROM (NEW."locale") OR OLD."accept_template_id" IS DISTINCT FROM (NEW."accept_template_id") OR OLD."ack_template_id" IS DISTINCT FROM (NEW."ack_template_id") OR OLD."reject_template_id" IS DISTINCT FROM (NEW."reject_template_id") OR OLD."update_template_id" IS DISTINCT FROM (NEW."update_template_id") OR OLD."question_template_id" IS DISTINCT FROM (NEW."question_template_id") OR OLD."landing_page_text" IS DISTINCT FROM (NEW."landing_page_text") OR OLD."featured_sessions_text" IS DISTINCT FROM (NEW."featured_sessions_text") OR OLD."plugins" IS DISTINCT FROM (NEW."plugins"))',
                    func='INSERT INTO "pretalx_auditlog_eventproxyevent" ("accept_template_id", "ack_template_id", "content_locale_array", "created", "custom_css", "custom_domain", "date_from", "date_to", "display_settings", "email", "feature_flags", "featured_sessions_text", "header_image", "id", "is_public", "landing_page_text", "locale", "locale_array", "logo", "mail_settings", "name", "organiser_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "plugins", "primary_color", "question_template_id", "reject_template_id", "review_settings", "slug", "timezone", "update_template_id") VALUES (NEW."accept_template_id", NEW."ack_template_id", NEW."content_locale_array", NEW."created", NEW."custom_css", NEW."custom_domain", NEW."date_from", NEW."date_to", NEW."display_settings", NEW."email", NEW."feature_flags", NEW."featured_sessions_text", NEW."header_image", NEW."id", NEW."is_public", NEW."landing_page_text", NEW."locale", NEW."locale_array", NEW."logo", NEW."mail_settings", NEW."name", NEW."organiser_id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."plugins", NEW."primary_color", NEW."question_template_id", NEW."reject_template_id", NEW."review_settings", NEW."slug", NEW."timezone", NEW."update_template_id"); RETURN NULL;',
                    hash="8c12a4c0e4bed1ce1ea0058928998dd8be1fb880",
                    operation="UPDATE",
                    pgid="pgtrigger_snapshot_update_c062e",
                    table="event_event",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="eventproxy",
            trigger=pgtrigger.compiler.Trigger(
                name="beforedelete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "pretalx_auditlog_eventproxyevent" ("accept_template_id", "ack_template_id", "content_locale_array", "created", "custom_css", "custom_domain", "date_from", "date_to", "display_settings", "email", "feature_flags", "featured_sessions_text", "header_image", "id", "is_public", "landing_page_text", "locale", "locale_array", "logo", "mail_settings", "name", "organiser_id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "plugins", "primary_color", "question_template_id", "reject_template_id", "review_settings", "slug", "timezone", "update_template_id") VALUES (OLD."accept_template_id", OLD."ack_template_id", OLD."content_locale_array", OLD."created", OLD."custom_css", OLD."custom_domain", OLD."date_from", OLD."date_to", OLD."display_settings", OLD."email", OLD."feature_flags", OLD."featured_sessions_text", OLD."header_image", OLD."id", OLD."is_public", OLD."landing_page_text", OLD."locale", OLD."locale_array", OLD."logo", OLD."mail_settings", OLD."name", OLD."organiser_id", _pgh_attach_context(), NOW(), \'beforedelete\', OLD."id", OLD."plugins", OLD."primary_color", OLD."question_template_id", OLD."reject_template_id", OLD."review_settings", OLD."slug", OLD."timezone", OLD."update_template_id"); RETURN NULL;',
                    hash="06e63f3282b7e45077d2dfc9dee189cf7c6d1b08",
                    operation="DELETE",
                    pgid="pgtrigger_beforedelete_a064f",
                    table="event_event",
                    when="AFTER",
                ),
            ),
        ),
    ]
