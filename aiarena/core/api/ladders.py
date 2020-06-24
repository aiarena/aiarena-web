import logging

from django.db.models import Max

from aiarena.core.models import Season, SeasonParticipation, Round

logger = logging.getLogger(__name__)


class Ladders:
    @staticmethod
    def get_season_ranked_participants(season: Season):
        # only return SeasonParticipations that are included in the most recent round
        last_round = Ladders.get_most_recent_round(season)
        return SeasonParticipation.objects.raw("select distinct csp.*"
                                        " from core_seasonparticipation csp"
                                        " left join core_bot cb on csp.bot_id = cb.id"
                                        " left join core_matchparticipation cmp on cb.id = cmp.bot_id"
                                        " left join core_match cm on cmp.match_id = cm.id"
                                        " where cm.round_id = %s"
                                        " order by elo desc", (last_round.id,))

    @staticmethod
    def get_most_recent_round(season: Season):
        return Round.objects.get(season=season, number=Round.objects.filter(season=season).aggregate(Max('number'))['number__max'])