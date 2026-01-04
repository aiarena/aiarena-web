from enum import Enum

from django.db import transaction
from django.utils import timezone

from aiarena.core.models import Match, MatchParticipation, Result

from .rounds import update_round_if_completed


def create(
    round,
    map,
    bot1,
    bot2,
    requested_by=None,
    bot1_use_data=None,
    bot1_update_data=None,
    bot2_use_data=None,
    bot2_update_data=None,
    require_trusted_arenaclient=True,
):
    with transaction.atomic():
        if bot1_use_data is None:
            bot1_use_data = bot1.bot_data_enabled
        if bot1_update_data is None:
            bot1_update_data = bot1.bot_data_enabled
        if bot2_use_data is None:
            bot2_use_data = bot2.bot_data_enabled
        if bot2_update_data is None:
            bot2_update_data = bot2.bot_data_enabled
        match = Match.objects.create(
            map=map, round=round, requested_by=requested_by, require_trusted_arenaclient=require_trusted_arenaclient
        )
        MatchParticipation.objects.create(
            match=match,
            participant_number=1,
            bot=bot1,
            use_bot_data=bot1_use_data,
            update_bot_data=bot1_update_data,
        )
        MatchParticipation.objects.create(
            match=match,
            participant_number=2,
            bot=bot2,
            use_bot_data=bot2_use_data,
            update_bot_data=bot2_update_data,
        )

        return match


# todo: this is used externally, so it probably shouldn't be here
class CancelResult(Enum):
    SUCCESS = 1
    MATCH_DOES_NOT_EXIST = 3
    RESULT_ALREADY_EXISTS = 2


def cancel(match_id, requesting_user):
    with transaction.atomic():
        try:
            # do this to lock the record
            # select_related() for the round data
            match = Match.objects.select_related("round").select_for_update(of=("self",)).get(pk=match_id)
        except Match.DoesNotExist:
            return CancelResult.MATCH_DOES_NOT_EXIST  # should basically not happen, but just in case

        if match.result_id:
            return CancelResult.RESULT_ALREADY_EXISTS

        match.result = Result.objects.create(type="MatchCancelled", game_steps=0, submitted_by=requesting_user)

        if not match.started:
            now = timezone.now()
            match.started = now
            match.first_started = now

        match.save()

        if match.round is not None:
            update_round_if_completed(match.round)
