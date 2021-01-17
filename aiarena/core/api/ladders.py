import logging

from django.db.models import Max

from aiarena.core.models import Competition, CompetitionParticipation, Round

logger = logging.getLogger(__name__)




class Ladders:
    @staticmethod
    def get_competition_ranked_participants(competition: Competition, amount=None):
        # only return SeasonParticipations that are included in the most recent round
        last_round = Ladders.get_most_recent_round(competition)

        if last_round is None:
            return CompetitionParticipation.objects.none()

        limit = f" LIMIT {amount}" if amount else ""
        query = "select distinct csp.id, elo, bot_id, win_perc, slug " \
                "from core_competitionparticipation csp " \
                "where competition_id = %s and bot_id in (" \
                "select cmp.bot_id " \
                "from core_match cm " \
                "join core_matchparticipation cmp on cm.id = cmp.match_id " \
                "where cm.round_id = %s)" \
                " order by csp.elo desc " + limit
        return CompetitionParticipation.objects.raw(query, (competition.id, last_round.id,))

    @staticmethod
    def get_most_recent_round(competition: Competition):
        try:
            return Round.objects.only('id').get(competition=competition, number=Round.objects.filter(competition=competition).aggregate(Max('number'))['number__max'])
        except Round.DoesNotExist:
            return None
