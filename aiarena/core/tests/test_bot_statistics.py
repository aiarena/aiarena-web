from io import StringIO

from django.core import serializers
from django.core.management import call_command
from django.test import TransactionTestCase

from aiarena.core.models import CompetitionParticipation, CompetitionBotMatchupStats
from aiarena.core.tests.test_mixins import FullDataSetMixin


class BotStatisticsTestCase(FullDataSetMixin, TransactionTestCase):
    def test_bot_stats_update_verses_recalculation(self):
        # At this point, the stats should have already been updated with
        # the match activity generated in FullDataSetMixin

        serialize_fields = [f.name for f in CompetitionBotMatchupStats._meta.get_fields()]
        # don't serialize these fields because they break our comparison
        serialize_fields.remove('updated')  # this is always different

        update_stats_json = dict()
        update_stats_json['global_stats'] = serializers.serialize('json',
                                                                  CompetitionParticipation.objects.order_by('id'))
        update_stats_json['matchup_stats'] = serializers.serialize('json',
                                                                   CompetitionBotMatchupStats.objects.defer(
                                                                       'updated').order_by('bot', 'opponent'),
                                                                   fields=serialize_fields)
        # update_stats_json['map_stats'] = serializers.serialize('json', CompetitionBotMapStats.objects.order_by('id'))

        out = StringIO()
        call_command('generatestats', '--allcompetitions', stdout=out)
        self.assertIn('Done', out.getvalue())

        recalc_stats_json = dict()
        recalc_stats_json['global_stats'] = serializers.serialize('json',
                                                                  CompetitionParticipation.objects.order_by('id'))
        recalc_stats_json['matchup_stats'] = serializers.serialize('json',
                                                                   CompetitionBotMatchupStats.objects.defer(
                                                                       'updated').order_by('bot', 'opponent'),
                                                                   fields=serialize_fields)
        # recalc_stats_json['map_stats'] = serializers.serialize('json', CompetitionBotMapStats.objects.order_by('id'))

        self.maxDiff = None  # required to print out large diffs
        self.assertEqual(update_stats_json, recalc_stats_json)
