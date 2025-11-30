from django.utils import timezone

from aiarena.core.models import Round


def update_round_if_completed(round: Round):
    """
    If all the matches have been run, mark this round as complete
    """
    if round.complete:  # check this first to avoid unnecessary DB queries
        raise ValueError(f"Round {round.id} is already complete")

    if _not_all_matches_have_a_result(round):
        return

    round.mark_complete(timezone.now())
    round.save()

    # After completing the round, try to close the competition
    round.competition.try_to_close()


def _not_all_matches_have_a_result(round: Round) -> bool:
    """
    Check whether there are any matches in the round that still lack a result.
    """
    return round.match_set.filter(result=None).exists()
