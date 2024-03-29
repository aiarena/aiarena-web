# Generated by Django 3.0.8 on 2020-12-31 09:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_remove_bot_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="map",
            name="game_mode",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, related_name="maps", to="core.GameMode"
            ),
            preserve_default=False,
        ),
    ]
