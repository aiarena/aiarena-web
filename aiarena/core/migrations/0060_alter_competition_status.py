# Generated by Django 3.2.16 on 2022-12-30 07:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0059_auto_20221229_1653"),
    ]

    operations = [
        migrations.AlterField(
            model_name="competition",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("created", "Created"),
                    ("frozen", "Frozen"),
                    ("paused", "Paused"),
                    ("open", "Open"),
                    ("closing", "Closing"),
                    ("closed", "Closed"),
                ],
                default="created",
                max_length=16,
            ),
        ),
    ]
