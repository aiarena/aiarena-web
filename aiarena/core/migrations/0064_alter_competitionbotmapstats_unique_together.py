# Generated by Django 3.2.16 on 2023-01-08 15:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0063_auto_20230108_1542"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="competitionbotmapstats",
            unique_together={("bot", "map")},
        ),
    ]
