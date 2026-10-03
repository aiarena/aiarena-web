from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.dispatch import receiver

from aiarena.core.services import competitions


if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from django.db import connection, transaction
from django.db.models import Min
from django.db.models.signals import pre_save
from django.utils import timezone

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
    def next_competition_match(arenaclient: ArenaClient, *, idle: bool = False):
        competition_ids = ACCoordinator._get_competition_priority_order()
        for competition_id in competition_ids:
            competition = Competition.objects.get(id=competition_id)
            # This excludes non-trusted clients from competitions requiring trusted infrastructure.
            # The idle pass uses the same check: a client that fails it never fills in.
            if not ACCoordinator._trusted_for_competition(arenaclient, competition):
                continue
            if not idle and not ACCoordinator._prefers_client(arenaclient, competition):
                ACCoordinator._log_limit_skip(competition)
                continue
            # this atomic block is done inside the for loop so that we don't hold onto a lock for a single competition
            with transaction.atomic():
                # this call will apply a select for update, so we do it inside an atomic block
                has_matches = competitions.check_has_matches_to_play_and_apply_locks(competition)

                if not has_matches:
                    continue
                # Re-read after the participant lock so two clients cannot both join a limit of one
                # on the preferred pass. The idle pass does not re-check: overflow is allowed.
                if not idle and not ACCoordinator._prefers_client(arenaclient, competition):
                    ACCoordinator._log_limit_skip(competition)
                    continue
                try:
                    match = matches.start_next_match_for_competition(arenaclient, competition)

                    return match
                except (
                    NoMaps,
                    NotEnoughAvailableBots,
                    MaxActiveRounds,
                    CompetitionPaused,
                    CompetitionClosing,
                ) as e:
                    logger.debug(f"Skipping competition {competition_id}: {e}")
                    continue

        return None

    @staticmethod
    def next_new_match(arenaclient: ArenaClient):
        requested_match = ACCoordinator.next_requested_match(arenaclient)

        if requested_match is not None:
            return requested_match
        # Preferred pass: respect the cap while this client has any other legal match.
        match = ACCoordinator.next_competition_match(arenaclient, idle=False)
        if match is not None:
            return match
        # Idle pass: nothing else to play, so a capped competition is fair game.
        return ACCoordinator.next_competition_match(arenaclient, idle=True)

    @staticmethod
    def _trusted_for_competition(arenaclient: ArenaClient, competition: Competition) -> bool:
        return arenaclient.trusted or competition.require_trusted_infrastructure == arenaclient.trusted

    @staticmethod
    def _log_limit_skip(competition: Competition):
        logger.debug(
            f"Skipping competition {competition.id}: "
            f"arena client limit {competition.arena_client_limit} prefers other clients."
        )

    @staticmethod
    def _prefers_client(arenaclient: ArenaClient, competition: Competition) -> bool:
        """True when this client may start a new ladder match on the preferred pass.

        A blank limit prefers every eligible client. Otherwise the window is the first
        ``arena_client_limit`` non-stale claimers, in the order they first started a
        ladder match. A short window admits the next poller.
        """
        limit = competition.arena_client_limit
        if limit is None:
            return True
        claim_order, non_stale = ACCoordinator._ladder_roster(competition)
        allowed = [client_id for client_id in claim_order if client_id in non_stale][:limit]
        if arenaclient.id in allowed:
            return True
        return len(non_stale) < limit

    @staticmethod
    def _ladder_roster(competition: Competition) -> tuple[list[int], set[int]]:
        """Claim order and the non-stale subset for one competition's ladder matches.

        Requested matches are not part of the roster. A claimer is non-stale while they
        hold an unfinished ladder match here, or submitted a result inside the match timeout.
        """
        ladder = Match.objects.filter(
            round__competition=competition,
            requested_by__isnull=True,
            assigned_to__isnull=False,
            started__isnull=False,
        )
        claim_order = list(
            ladder.values("assigned_to_id")
            .annotate(first_started=Min("started"))
            .order_by("first_started", "assigned_to_id")
            .values_list("assigned_to_id", flat=True)
        )
        if not claim_order:
            return [], set()

        cutoff = timezone.now() - config.TIMEOUT_MATCHES_AFTER
        active = set(ladder.filter(result__isnull=True).values_list("assigned_to_id", flat=True))
        recent = set(
            ladder.filter(result__isnull=False, result__created__gte=cutoff).values_list("assigned_to_id", flat=True)
        )
        return claim_order, active | recent

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

    @staticmethod
    def _get_competition_priority_order():
        """
        Returns a list of competition ids in priority order with respect to the current number of active participants
         in each competition verses each competition's share of the most recent 100 matches.
         In otherwords, campetitions with higher active participant counts should play more matches overall.
        :return:
        """

        competition_priority_order = cache.get("competition_priority_order")
        if not competition_priority_order:
            with connection.cursor() as cursor:
                # I don't know why but for some reason CTEs didn't work so here; have a massive query.
                cursor.execute(
                    """
                    select perc_active.competition_id
                    from (select competition_id, 
                    competition_participations.competition_participations_cnt / cast(total_active_cnt as float) as perc_active
                          from (select cp.competition_id, count(cp.competition_id) competition_participations_cnt
                                from core_competitionparticipation cp
                                         join core_competition cc on cp.competition_id = cc.id
                                where cp.active
                                  and cc.status in ('open', 'closing', 'paused')
                                group by cp.competition_id) as competition_participations
                                   join
                               (select count(*) total_active_cnt
                                from core_competitionparticipation cp
                                         join core_competition cc on cp.competition_id = cc.id
                                where cp.active
                                  and cc.status in ('open', 'closing', 'paused')) as competition_participations_total on 1=1) as perc_active
                             left join
                         (select competition_id, perc_recent_matches_cnt / cast(recent_matches_total_cnt as float) as perc_recent_matches
                          from (select competition_id,
                                       count(competition_id)       perc_recent_matches_cnt,
                                       (select count(*)
                                        from (select competition_id
                                              from core_match cm
                                                       join core_round cr on cm.round_id = cr.id
                                                       join core_competition cc on cr.competition_id = cc.id
                                              where cm.started is not null
                                                and cc.status in ('open', 'closing', 'paused')
                                              order by cm.started desc
                                              limit 100) matches2) recent_matches_total_cnt
                                from (select competition_id
                                      from core_match cm
                                               join core_round cr on cm.round_id = cr.id
                                               join core_competition cc on cr.competition_id = cc.id
                                      where cm.started is not null
                                        and cc.status in ('open', 'closing', 'paused')
                                      order by cm.started desc
                                      limit 100) matches
                                group by competition_id) as recent_matches) as perc_recent_matches
                         on perc_recent_matches.competition_id = perc_active.competition_id
                    order by COALESCE(perc_recent_matches, 0) - perc_active
                """
                )
                competition_priority_order = [row[0] for row in cursor.fetchall()]  # return competition ids
                cache.set(
                    "competition_priority_order",
                    competition_priority_order,
                    config.COMPETITION_PRIORITY_ORDER_CACHE_TIME,
                )

        return competition_priority_order


@receiver(pre_save, sender=Competition)
def post_save_competition(sender, instance, **kwargs):
    # if it's not a new instance...
    if instance.id is not None:
        previous = Competition.objects.get(id=instance.id)
        if previous.status != instance.status and cache.has_key("competition_priority_order"):
            cache.delete(
                "competition_priority_order"
            )  # if the status changed, bust our competition_priority_order cache
