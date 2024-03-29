# Generated by Django 3.0.8 on 2020-12-24 18:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_auto_20201219_1341"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[("WEBSITE_USER", "Website User"), ("ARENA_CLIENT", "Arena Client"), ("SERVICE", "Service")],
                default="WEBSITE_USER",
                max_length=16,
            ),
        ),
    ]
