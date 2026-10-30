from django.db import migrations


def backfill_deletion_allowed(apps, schema_editor):
    # Competitions created by the old code during the previous rollout have NULL here.
    Competition = apps.get_model("core", "Competition")
    Competition.objects.filter(deletion_allowed__isnull=True).update(deletion_allowed=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0089_competition_deletion_allowed"),
    ]

    operations = [
        migrations.RunPython(backfill_deletion_allowed, migrations.RunPython.noop),
    ]
