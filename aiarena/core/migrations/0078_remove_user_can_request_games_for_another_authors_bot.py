# Generated by Django 4.2.16 on 2024-11-03 08:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0077_update_relative_result"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="can_request_games_for_another_authors_bot",
        ),
    ]