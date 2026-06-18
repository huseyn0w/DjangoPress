# Phase 8.1 — django-parler conversion, step 2 of 3.
#
# Copy each row's original (single-language) content from the renamed *_old columns
# into a translation row in the default language, so no data is lost when those
# columns are dropped in 0004. Reverse writes the default-language translation back
# onto the *_old columns.

from django.conf import settings
from django.db import migrations

# base model -> (translation model, {translation field: base *_old field}).
TRANSLATED_FIELDS = {
    "Category": ("CategoryTranslation", {"name": "name_old", "description": "description_old"}),
    "Tag": ("TagTranslation", {"name": "name_old"}),
    "Post": ("PostTranslation", {"title": "title_old", "excerpt": "excerpt_old", "body": "body_old"}),
    "Page": ("PageTranslation", {"title": "title_old", "body": "body_old"}),
}


def _default_language() -> str:
    return getattr(settings, "PARLER_DEFAULT_LANGUAGE_CODE", None) or settings.LANGUAGE_CODE


def forwards(apps, schema_editor):
    language = _default_language()
    for base_name, (trans_name, field_map) in TRANSLATED_FIELDS.items():
        Base = apps.get_model("content", base_name)
        Translation = apps.get_model("content", trans_name)
        for obj in Base.objects.all():
            values = {tfield: getattr(obj, ofield) for tfield, ofield in field_map.items()}
            Translation.objects.update_or_create(
                master=obj, language_code=language, defaults=values
            )


def backwards(apps, schema_editor):
    language = _default_language()
    for base_name, (trans_name, field_map) in TRANSLATED_FIELDS.items():
        Base = apps.get_model("content", base_name)
        Translation = apps.get_model("content", trans_name)
        for obj in Base.objects.all():
            translation = (
                Translation.objects.filter(master=obj, language_code=language).first()
                or Translation.objects.filter(master=obj).first()
            )
            if translation:
                for tfield, ofield in field_map.items():
                    setattr(obj, ofield, getattr(translation, tfield))
                obj.save(update_fields=list(field_map.values()))


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_create_translation_tables"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
