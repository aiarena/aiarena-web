# Generated by Django 4.2.13 on 2024-06-29 12:18

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import OuterRef, Subquery


def populate_match_result(apps, schema_editor):
    Match = apps.get_model("core", "Match")
    Result = apps.get_model("core", "Result")

    Match.objects.update(
        result=Subquery(Result.objects.filter(match=OuterRef("pk")).values("id")[:1]),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0074_user_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="match",
            name="result",
            field=models.OneToOneField(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="+", to="core.result"
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="match",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name="result_old", to="core.match"
            ),
        ),
        migrations.RunPython(populate_match_result, reverse_code=migrations.RunPython.noop),
    ]
