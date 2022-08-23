# Generated by Django 3.2.9 on 2022-08-20 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patreon', '0004_patreonaccountbind_patreon_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatreonUnlinkedDiscordUID',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patreon_user_id', models.CharField(max_length=64, unique=True)),
                ('discord_uid', models.CharField(max_length=64, unique=True)),
            ],
        ),
    ]
