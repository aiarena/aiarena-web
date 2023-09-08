import math

from aiarena.core.models import Match


class MatchInterestAnalyzer:
    def __init__(self, elo_diff_rating_modifier: float, combined_elo_rating_divisor: int):
        self.elo_diff_rating_modifier = elo_diff_rating_modifier
        self.combined_elo_rating_divisor = combined_elo_rating_divisor

    def rate_match(self, match: Match) -> float:
        """Attempts to rate the match based on how "interesting" it is."""

        # Any match that didn't fully play out we consider not interesting.
        if match.result.type not in [
            "Player1Win",
            "Player2Win",
            "Player1Surrender",
            "Player2Surrender",
        ]:
            return -1.0

        # prefer higher ELO matches
        # todo: make this rank instead?
        avg_elo = (match.participant1.starting_elo + match.participant2.starting_elo) / 2
        elo_height_rating = 1 / (1 + math.exp(avg_elo / self.combined_elo_rating_divisor)) - 0.5

        # avoid large elo differences unless it's an upset
        elo_difference_rating = 0
        if match.matchparticipation_set.order_by("starting_elo")[0].bot != match.result.winner:
            elo_diff = abs(match.participant1.starting_elo - match.participant2.starting_elo)
            elo_difference_rating = self.elo_diff_rating_modifier**elo_diff - 1

        # average them out
        return (elo_height_rating + elo_difference_rating) / 2
