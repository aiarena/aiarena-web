import logging

from django.db.models import Max

from aiarena.core.models import Season, SeasonParticipation, Round

logger = logging.getLogger(__name__)


class Ladders:
    @staticmethod
    def get_season_ranked_participants(season: Season):
        last_round_numer = Round.objects.filter(season=season).aggregate(Max('number'))
        return SeasonParticipation.objects.filter(season=season, season__round__number=last_round_numer['number__max']).order_by('-elo')

