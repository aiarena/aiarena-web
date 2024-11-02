import logging

from django.db.models import Case, Max, When

from aiarena.core.models import Competition, CompetitionParticipation, Round


logger = logging.getLogger(__name__)


class Ladders:
    @staticmethod
    def _get_competition_participants(competition: Competition):
        return (
            CompetitionParticipation.objects.only(
                "id", "bot__id", "division_num", "elo", "win_perc", "slug", "in_placements"
            )
            .filter(competition=competition)
            .annotate(
                ranked_division_num=Case(
                    When(division_num=CompetitionParticipation.DEFAULT_DIVISION, then=competition.n_divisions + 1),
                    default="division_num",
                ),
                capped_match_count=Case(
                    When(in_placements=False, then=competition.n_placements + 1),
                    When(in_placements=True, match_count__gt=competition.n_placements, then=competition.n_placements),
                    default="match_count",
                ),
            )
            .order_by("ranked_division_num", "-capped_match_count", "-elo")
        )

    @staticmethod
    def get_competition_display_full_rankings(competition: Competition):
        """
        Get the participants for a competition for the purpose of displaying a full rankings list.
        """
        if competition.status == "closed":
            all_participants = Ladders.get_competition_last_round_participants(competition)
        else:
            all_participants = Ladders.get_competition_ranked_participants(competition, include_placements=True)
        return all_participants

    @staticmethod
    def get_competition_ranked_participants(competition: Competition, amount=None, include_placements=False):
        """
        Get raw ranked participants for a competition, with optional amount and whether to include placements.
        """
        participants = Ladders._get_competition_participants(competition).filter(active=True)
        if not include_placements:
            # Keep those out of placement and have a division
            participants = participants.filter(
                in_placements=False, division_num__gte=CompetitionParticipation.MIN_DIVISION
            )
        return participants if amount is None else participants[:amount]

    @staticmethod
    def get_competition_last_round_participants(competition: Competition, amount=None):
        participants = Ladders._get_competition_participants(competition).filter(
            participated_in_most_recent_round=True, division_num__gte=CompetitionParticipation.MIN_DIVISION
        )

        return participants if amount is None else participants[:amount]

    @staticmethod
    def get_most_recent_round(competition: Competition):
        try:
            return Round.objects.only("id").get(
                competition=competition,
                number=Round.objects.filter(competition=competition).aggregate(Max("number"))["number__max"],
            )
        except Round.DoesNotExist:
            return None
