from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Bot, Match


class Command(BaseCommand):
    help = 'Requests a match for the specified bot.'

    def add_arguments(self, parser):
        parser.add_argument('botid', type=int, help="The id of the bot to request a match for.")
        parser.add_argument('--opponentid', type=int, default=None,
                            help="The id of the opponent to fight. Default: A random active bot")

    def handle(self, *args, **options):
        bot = Bot.objects.get(pk=options['botid'])  # todo: catch bot missing
        opponent = None
        if options['opponentid'] is not None:
            opponent = Bot.objects.select_for_update().get(pk=options['opponent']) # todo: catch bot missing

        # if opponent is none a random one gets chosen
        match = Match.request_bot_match(bot, opponent)
        self.stdout.write(self.style.SUCCESS('Successfully requested match. Match ID: {0}'.format(match.id)))

