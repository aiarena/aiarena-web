# Generated by Django 4.2 on 2024-01-08 14:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0073_auto_20231019_1411"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="note",
            field=models.TextField(blank=True, null=True),
        ),
    ]