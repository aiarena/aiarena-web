from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING

from aiarena.core.services import competitions


if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from django.db import transaction
from django.db.models import Count, Q

from constance import config

from aiarena.core.exceptions import (
    CompetitionClosing,
    CompetitionPaused,
    MaxActiveRounds,
    NoMaps,
    NotEnoughAvailableBots,
)
from aiarena.core.models import Competition, Match
from aiarena.core.services import matches

from .exceptions import LadderDisabled


logger = logging.getLogger(__name__)

SCHEDULABLE_COMPETITION_STATUSES = ("open", "closing", "paused")
RECENT_MATCH_WINDOW = 100


def rank_competitions(entitlements: Mapping[int, int], recent_competition_ids: Iterable[int]) -> list[int]:
    """Competition ids ordered by who is furthest below their entitled share of new matches.

    ``entitlements`` maps competition id to active participants times weight. Competitions are sorted by
    recent match count per entitlement (lowest first), then larger entitlement, then id. A competition
    with no positive entitlement sorts after all others. Ids in ``recent_competition_ids`` that are not
    in ``entitlements`` are ignored.
    """
    recent_counts = Counter(recent_competition_ids)

    def sort_key(competition_id: int):
        entitlement = entitlements[competition_id]
        if entitlement <= 0:
            return 1, 0.0, 0, competition_id
        return 0, recent_counts[competition_id] / entitlement, -entitlement, competition_id

    return sorted(entitlements, key=sort_key)


def competition_priority_order() -> list[int]:
    """Ids of the competitions with active participants, in the order new ladder matches should be offered.

    Computed on every call. The recent window covers far less time than a useful cache lifetime, so a cached
    order goes stale and lets whichever competition is on top take every client.
    """
    schedulable = (
        Competition.objects.filter(status__in=SCHEDULABLE_COMPETITION_STATUSES)
        .annotate(active_participants=Count("participations", filter=Q(participations__active=True)))
        .filter(active_participants__gte=1)
        .values_list("id", "active_participants", "scheduling_weight")
    )
    entitlements = {
        competition_id: active_participants * (weight if weight is not None else Competition.DEFAULT_SCHEDULING_WEIGHT)
        for competition_id, active_participants, weight in schedulable
    }

    recent_competition_ids = list(
        Match.objects.filter(started__isnull=False, round__competition__status__in=SCHEDULABLE_COMPETITION_STATUSES)
        .order_by("-started")
        .values_list("round__competition_id", flat=True)[:RECENT_MATCH_WINDOW]
    )
    return rank_competitions(entitlements, recent_competition_ids)


class ACCoordinator:
    """Coordinates all the Arena Clients and which matches they play."""

    @staticmethod
    def next_requested_match(arenaclient: ArenaClient):
        # REQUESTED MATCHES
        with transaction.atomic():
            match = matches.attempt_to_start_a_requested_match(arenaclient)

            if match is not None:
                return match  # a match was found - we're done
        return None

    @staticmethod
    def next_competition_match(arenaclient: ArenaClient):
        for competition_id in competition_priority_order():
            competition = Competition.objects.get(id=competition_id)
            # This excludes non-trusted clients from competitions requiring trusted infrastructure.
            if not ACCoordinator._trusted_for_competition(arenaclient, competition):
                continue
            match = ACCoordinator._try_start_match(arenaclient, competition)
            if match is not None:
                return match

        return None

    @staticmethod
    def _try_start_match(arenaclient: ArenaClient, competition: Competition) -> Match | None:
        # this atomic block is done per competition so that we don't hold onto a lock for a single competition
        with transaction.atomic():
            # this call will apply a select for update, so we do it inside an atomic block
            if not competitions.check_has_matches_to_play_and_apply_locks(competition):
                return None
            try:
                return matches.start_next_match_for_competition(arenaclient, competition)
            except (
                NoMaps,
                NotEnoughAvailableBots,
                MaxActiveRounds,
                CompetitionPaused,
                CompetitionClosing,
            ) as e:
                logger.debug(f"Skipping competition {competition.id}: {e}")
                return None

    @staticmethod
    def next_new_match(arenaclient: ArenaClient):
        requested_match = ACCoordinator.next_requested_match(arenaclient)

        if requested_match is not None:
            return requested_match
        return ACCoordinator.next_competition_match(arenaclient)

    @staticmethod
    def _trusted_for_competition(arenaclient: ArenaClient, competition: Competition) -> bool:
        return arenaclient.trusted or competition.require_trusted_infrastructure == arenaclient.trusted

    @staticmethod
    def next_match(arenaclient: ArenaClient, only_unfinished_matches: bool) -> Match | None:
        if not config.LADDER_ENABLED:
            raise LadderDisabled()

        if config.REISSUE_UNFINISHED_MATCHES:
            # Check for any unfinished matches assigned to this user. If any are present, return that.
            unfinished_matches = list(
                Match.objects.only("id", "map")
                .filter(
                    result=None,
                    started__isnull=False,
                    assigned_to=arenaclient,
                )
                .order_by("round_id")
            )

            if len(unfinished_matches) > 0:
                return unfinished_matches[0]  # todo: re-set started time?
            if only_unfinished_matches:
                return None  # Return None so we don't try to start a new match
        # Trying a new match
        return ACCoordinator.next_new_match(arenaclient)
