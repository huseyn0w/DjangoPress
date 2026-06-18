# Phase 8.1 — django-parler conversion, step 1 of 3.
#
# Non-destructive and fully portable (Django operations only, no raw SQL):
#   1. Rename the existing single-language columns aside (title -> title_old, ...).
#      parler will not allow a concrete `title` and a translated `title` to coexist
#      in the same model state, so the originals must step out of the way by name
#      before the translation tables are created.
#   2. Create the per-language translation tables.
#   3. Add the language_code column to revisions.
# The *_old columns keep the data so 0003 can copy it into the default-language
# translation rows before 0004 drops them.

import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        # 1. Move the original columns aside so their names are free for parler.
        migrations.RenameField("post", "title", "title_old"),
        migrations.RenameField("post", "excerpt", "excerpt_old"),
        migrations.RenameField("post", "body", "body_old"),
        migrations.RenameField("page", "title", "title_old"),
        migrations.RenameField("page", "body", "body_old"),
        migrations.RenameField("category", "name", "name_old"),
        migrations.RenameField("category", "description", "description_old"),
        migrations.RenameField("tag", "name", "name_old"),
        # 2. Update Meta (ordering by a translated field is no longer possible).
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name": "category", "verbose_name_plural": "categories"},
        ),
        migrations.AlterModelOptions(
            name="page",
            options={"verbose_name": "page", "verbose_name_plural": "pages"},
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={"verbose_name": "tag", "verbose_name_plural": "tags"},
        ),
        # 3. Revisions gain a language column (each snapshot belongs to one language).
        migrations.AddField(
            model_name="pagerevision",
            name="language_code",
            field=models.CharField(default="en", max_length=15, verbose_name="language"),
        ),
        migrations.AddField(
            model_name="postrevision",
            name="language_code",
            field=models.CharField(default="en", max_length=15, verbose_name="language"),
        ),
        migrations.CreateModel(
            name="CategoryTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(db_index=True, max_length=15, verbose_name="Language"),
                ),
                ("name", models.CharField(max_length=100, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="content.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "category Translation",
                "db_table": "content_category_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="content_category_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PageTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(db_index=True, max_length=15, verbose_name="Language"),
                ),
                ("title", models.CharField(max_length=200, verbose_name="title")),
                ("body", models.TextField(blank=True, verbose_name="body")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="content.page",
                    ),
                ),
            ],
            options={
                "verbose_name": "page Translation",
                "db_table": "content_page_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="content_page_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PostTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(db_index=True, max_length=15, verbose_name="Language"),
                ),
                ("title", models.CharField(max_length=200, verbose_name="title")),
                ("excerpt", models.TextField(blank=True, verbose_name="excerpt")),
                ("body", models.TextField(blank=True, verbose_name="body")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="content.post",
                    ),
                ),
            ],
            options={
                "verbose_name": "post Translation",
                "db_table": "content_post_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"),
                        name="content_post_translation_uniq_lang",
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="TagTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "language_code",
                    models.CharField(db_index=True, max_length=15, verbose_name="Language"),
                ),
                ("name", models.CharField(max_length=50, verbose_name="name")),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="content.tag",
                    ),
                ),
            ],
            options={
                "verbose_name": "tag Translation",
                "db_table": "content_tag_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("language_code", "master"), name="content_tag_translation_uniq_lang"
                    )
                ],
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
    ]
