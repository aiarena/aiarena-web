# Generated by Django 3.2.16 on 2023-01-06 10:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0060_alter_competition_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="BotCrashLimitAlert",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("logged_at", models.DateTimeField(auto_now_add=True)),
                (
                    "triggering_match_participation",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="core.matchparticipation"),
                ),
            ],
        ),
    ]
