# Phase 8.1 — django-parler conversion, step 3 of 3.
#
# Now that 0003 has copied the content into translation rows, drop the renamed
# *_old columns from the base tables. Reverse re-creates them (empty); running
# 0003 backwards then refills them from the default-language translation.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0003_copy_translations"),
    ]

    operations = [
        migrations.RemoveField(model_name="category", name="name_old"),
        migrations.RemoveField(model_name="category", name="description_old"),
        migrations.RemoveField(model_name="page", name="title_old"),
        migrations.RemoveField(model_name="page", name="body_old"),
        migrations.RemoveField(model_name="post", name="title_old"),
        migrations.RemoveField(model_name="post", name="excerpt_old"),
        migrations.RemoveField(model_name="post", name="body_old"),
        migrations.RemoveField(model_name="tag", name="name_old"),
    ]
