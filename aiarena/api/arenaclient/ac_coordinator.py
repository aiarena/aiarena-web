from __future__ import annotations

from typing import TYPE_CHECKING

from aiarena.core.api.competitions import Competitions

if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from constance import config
from django.db import transaction
from django.db.models import F

from aiarena.api.arenaclient.exceptions import LadderDisabled, NoCurrentlyAvailableCompetitions
from aiarena.core.api import Matches
from aiarena.core.models import Match, Competition

logger = logging.getLogger(__name__)


class ACCoordinator:
    """Coordinates all the Arena Clients and which matches they play."""

    @staticmethod
    def next_competition_match(arenaclient: ArenaClient):
        for competition in Competition.objects.filter(status__in=['open', 'closing', 'paused']):
            # this atomic block is done inside the for loop so that we don't hold onto a lock for a single competition
            with transaction.atomic():
                # this call will apply a select for update, so we do it inside an atomic block
                if Competitions.check_has_matches_to_play_and_apply_locks(competition):
                    return Matches.start_next_match(arenaclient, competition)

        raise NoCurrentlyAvailableCompetitions()

    @staticmethod
    def next_match(arenaclient: ArenaClient) -> Match:
        if config.LADDER_ENABLED:
            try:
                if config.REISSUE_UNFINISHED_MATCHES:
                    # Check for any unfinished matches assigned to this user. If any are present, return that.
                    unfinished_matches = Match.objects.only('id', 'map') \
                        .filter(started__isnull=False, assigned_to=arenaclient,
                                result__isnull=True).order_by(F('round_id').asc())
                    if unfinished_matches.count() > 0:
                        return unfinished_matches[0]  # todo: re-set started time?
                    else:
                        return ACCoordinator.next_competition_match(arenaclient)
                else:
                    return ACCoordinator.next_competition_match(arenaclient)
            except Exception as e:
                logger.exception("Exception while processing request for match.")
                raise
        else:
            raise LadderDisabled()
