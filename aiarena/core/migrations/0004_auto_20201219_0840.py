# Generated by Django 3.0.8 on 2020-12-18 22:10

from django.db import migrations

from aiarena.core.models import Competition
from aiarena.core.models.game import Game
from aiarena.core.models.game_type import GameMode


def update_name(apps, schema_editor):
    # set initial names
    for competition in Competition.objects.all():
        competition.name = f"AI Arena - Season {competition.id}"
        competition.save()

def create_game_mode(apps, schema_editor):
    """ If these is an existing competition, it will need a game and game mode """
    if Competition.objects.count() > 0:
        game = Game.objects.create(name='StarCraft II')
        GameMode.objects.create(name='Melee', game=game)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201219_0827'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Season',
            new_name='Competition',
        ),
        migrations.RunPython(update_name),
        migrations.RunPython(create_game_mode),
    ]