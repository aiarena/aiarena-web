from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Match, Result

def cancel(match_id, requesting_user):
    with transaction.atomic():
        try:
            # do this to lock the record
            # select_related() for the round data
            match = Match.objects.select_related("round").select_for_update(of=("self",)).get(pk=match_id)
        except Match.DoesNotExist:
            return Match.CancelResult.MATCH_DOES_NOT_EXIST  # should basically not happen, but just in case

        if Result.objects.filter(match=match).count() > 0:
            return Match.CancelResult.RESULT_ALREADY_EXISTS

        Result.objects.create(match=match, type="MatchCancelled", game_steps=0, submitted_by=requesting_user)

        if not match.started:
            now = timezone.now()
            match.started = now
            match.first_started = now
            match.save()

        if match.round is not None:
            match.round.update_if_completed()