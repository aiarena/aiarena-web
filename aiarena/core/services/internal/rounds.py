from django.utils import timezone

from aiarena.core.models import Round


def update_round_if_completed(round: Round):
    """
    If all the matches have been run, mark this round as complete
    """
    if round.complete:  # round.mark_complete() will check this, but do it here to avoid unnecessary DB queries
        # Nothing should call this method on an already completed round. Highlight the bug.
        raise ValueError(f"Round {round.id} is already complete")

    if _not_all_matches_have_a_result(round):
        return

    round.mark_complete(timezone.now())
    round.save(update_fields=["complete", "finished"])

    # After completing the round, try to close the competition
    round.competition.try_to_close()


def _not_all_matches_have_a_result(round: Round) -> bool:
    """
    Check whether there are any matches in the round that still lack a result.
    """
    return round.match_set.filter(result=None).exists()
