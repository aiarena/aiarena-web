import json
from io import StringIO

from django.core import serializers
from django.core.management import call_command
from django.test import TransactionTestCase

from aiarena.core.models import CompetitionBotMapStats, CompetitionBotMatchupStats, CompetitionParticipation
from aiarena.core.tests.test_mixins import FullDataSetMixin


class BotStatisticsTestCase(FullDataSetMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        call_command("generatestats")

    def test_bot_stats_update_verses_recalculation(self):
        # At this point, the stats should have already been updated with
        # the match activity generated in FullDataSetMixin

        update_stats_json = dict()

        global_stats = json.loads(serializers.serialize("json", CompetitionParticipation.objects.order_by("id")))
        for global_stat in global_stats:
            del global_stat["fields"]["elo_graph"]
            del global_stat["fields"]["elo_graph_update_plot"]
            del global_stat["fields"]["winrate_vs_duration_graph"]
        update_stats_json["global_stats"] = json.dumps(global_stats)

        matchup_stats = list(CompetitionBotMatchupStats.objects.order_by("bot", "opponent").values())
        for matchup_stat in matchup_stats:
            # these won't match, so remove them
            del matchup_stat["id"]
            del matchup_stat["updated"]
        update_stats_json["matchup_stats"] = json.dumps(matchup_stats)

        map_stats = list(CompetitionBotMapStats.objects.order_by("bot", "map").values())
        for map_stat in map_stats:
            # these won't match, so remove them
            del map_stat["id"]
            del map_stat["updated"]
        update_stats_json["map_stats"] = json.dumps(map_stats)

        out = StringIO()
        call_command("generatestats", "--allcompetitions", stdout=out)
        self.assertIn("Done", out.getvalue())

        recalc_stats_json = dict()
        global_stats = json.loads(serializers.serialize("json", CompetitionParticipation.objects.order_by("id")))
        for global_stat in global_stats:
            del global_stat["fields"]["elo_graph"]
            del global_stat["fields"]["elo_graph_update_plot"]
            del global_stat["fields"]["winrate_vs_duration_graph"]
        recalc_stats_json["global_stats"] = json.dumps(global_stats)

        matchup_stats = list(CompetitionBotMatchupStats.objects.order_by("bot", "opponent").values())
        for matchup_stat in matchup_stats:
            # these won't match, so remove them
            del matchup_stat["id"]
            del matchup_stat["updated"]
        recalc_stats_json["matchup_stats"] = json.dumps(matchup_stats)

        map_stats = list(CompetitionBotMapStats.objects.order_by("bot", "map").values())
        for map_stat in map_stats:
            # these won't match, so remove them
            del map_stat["id"]
            del map_stat["updated"]
        recalc_stats_json["map_stats"] = json.dumps(map_stats)

        self.assertEqual(update_stats_json, recalc_stats_json)
