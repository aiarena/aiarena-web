from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from aiarena.core.exceptions import BotNotInMatchException
from aiarena.core.models import Match, Result


class Command(BaseCommand):
    help = 'Registers an InitializationError result for all current matches.'

    def add_arguments(self, parser):
        parser.add_argument('match_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        with transaction.atomic():
            for match_id in options['match_ids']:
                try:
                    match = Match.objects.select_for_update().get(pk=match_id)
                except Match.DoesNotExist:
                    raise CommandError('Match "%s" does not exist' % match_id)

                if Result.objects.filter(match=match).count() > 0:
                    raise CommandError('A result already exists for match "%s"' % match_id)

                Result.objects.create(match=match, type='InitializationError', duration=0)

                # attempt to kick the bots from the match
                if match.started:
                    try:
                        bot1 = match.participant_set.select_related().select_for_update().get(participant_number=1).bot
                        bot1.leave_match(match_id)
                    except BotNotInMatchException:
                        self.stdout.write(
                            'WARNING! Match "{1}": Participant 1 bot "{0}" was not registered as in this match, despite the match having started.'.format(
                                bot1.id, match_id))
                    try:
                        bot2 = match.participant_set.select_related().select_for_update().get(participant_number=2).bot
                        bot2.leave_match(match_id)
                    except BotNotInMatchException:
                        self.stdout.write(
                            'WARNING! Match "{1}": Participant 2 bot "{0}" was not registered as in this match, despite the match having started.'.format(
                                bot2.id, match_id))
                else:
                    match.started = timezone.now()
                    match.save()

                self.stdout.write(
                    self.style.SUCCESS('Successfully marked match "%s" with an InitializationError' % match_id))
