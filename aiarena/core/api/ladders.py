import logging

from django.db.models import Max, Case, When

from aiarena.core.models import Competition, CompetitionParticipation, Round

logger = logging.getLogger(__name__)




class Ladders:
    @staticmethod
    def get_competition_ranked_participants(competition: Competition, amount=None):
        participants = (CompetitionParticipation.objects
            .only("id","bot__id","division_num","elo","win_perc","slug","in_placements")
            .annotate(
                capped_match_count=Case(
                    When(in_placements=True, then=competition.n_placements+1),
                    default='match_count'
                )
            )
            .filter(competition=competition, active=True, in_placements=False)
            .order_by("division_num", '-capped_match_count', '-elo'))
        return participants if amount is None else participants[:amount]

    @staticmethod
    def get_most_recent_round(competition: Competition):
        try:
            return Round.objects.only('id').get(competition=competition, number=Round.objects.filter(competition=competition).aggregate(Max('number'))['number__max'])
        except Round.DoesNotExist:
            return None
