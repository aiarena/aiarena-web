from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from constance import config
from django.db import transaction
from django.db.models import F

from aiarena.api.arenaclient.exceptions import LadderDisabled
from aiarena.core.api import Matches
from aiarena.core.models import Match, Competition

logger = logging.getLogger(__name__)


class ACCoordinator:
    """Coordinates all the Arena Clients and which matches they play."""

    @staticmethod
    def get_random_competition():
        return Competition.objects.filter(status__in=['open', 'closing']).order_by('?')[0]

    @staticmethod
    def next_match(arenaclient: ArenaClient) -> Match:
        if config.LADDER_ENABLED:
            with transaction.atomic():
                try:
                    if config.REISSUE_UNFINISHED_MATCHES:
                        # Check for any unfinished matches assigned to this user. If any are present, return that.
                        unfinished_matches = Match.objects.only('id', 'map') \
                            .filter(started__isnull=False, assigned_to=arenaclient,
                                    result__isnull=True).order_by(F('round_id').asc())
                        if unfinished_matches.count() > 0:
                            return unfinished_matches[0]  # todo: re-set started time?
                        else:
                            return Matches.start_next_match(arenaclient, ACCoordinator.get_random_competition())
                    else:
                        return Matches.start_next_match(arenaclient, ACCoordinator.get_random_competition())
                except Exception as e:
                    logger.exception("Exception while processing request for match.")
                    raise
        else:
            raise LadderDisabled()
