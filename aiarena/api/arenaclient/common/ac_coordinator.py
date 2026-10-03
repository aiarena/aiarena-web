from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.dispatch import receiver

from aiarena.core.services import competitions


if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from django.db import connection, transaction
from django.db.models import Min, Q
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
    def next_competition_match(arenaclient: ArenaClient):
        competition_ids = ACCoordinator._get_competition_priority_order()
        # Competitions whose arena client limit prefers other clients. They are only tried once every
        # preferred competition has been tried, so a client with nothing else to play can still fill in.
        deferred: list[Competition] = []
        for competition_id in competition_ids:
            competition = Competition.objects.get(id=competition_id)
            # This excludes non-trusted clients from competitions requiring trusted infrastructure.
            # Deferred competitions get the same check: a client that fails it never fills in.
            if not ACCoordinator._trusted_for_competition(arenaclient, competition):
                continue
            if not ACCoordinator._prefers_client(arenaclient, competition):
                ACCoordinator._log_limit_skip(competition)
                deferred.append(competition)
                continue
            match = ACCoordinator._try_start_match(arenaclient, competition, enforce_limit=True)
            if match is not None:
                return match

        for competition in deferred:
            match = ACCoordinator._try_start_match(arenaclient, competition, enforce_limit=False)
            if match is not None:
                return match

        return None

    @staticmethod
    def _try_start_match(arenaclient: ArenaClient, competition: Competition, *, enforce_limit: bool) -> Match | None:
        # this atomic block is done per competition so that we don't hold onto a lock for a single competition
        with transaction.atomic():
            # this call will apply a select for update, so we do it inside an atomic block
            if not competitions.check_has_matches_to_play_and_apply_locks(competition):
                return None
            # Re-read after the participant lock so two clients cannot both join a limit of one.
            # Deferred (overflow) attempts skip this: they are allowed past the limit.
            if enforce_limit and not ACCoordinator._prefers_client(arenaclient, competition):
                ACCoordinator._log_limit_skip(competition)
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
    def _log_limit_skip(competition: Competition):
        logger.debug(
            f"Skipping competition {competition.id}: "
            f"arena client limit {competition.arena_client_limit} prefers other clients."
        )

    @staticmethod
    def _prefers_client(arenaclient: ArenaClient, competition: Competition) -> bool:
        """True when this client may start a new ladder match while preferred competitions are tried.

        A blank limit prefers every eligible client. Otherwise the window is the first
        ``arena_client_limit`` active claimers, in the order they started their earliest active
        ladder match. A short window admits the next poller.
        """
        limit = competition.arena_client_limit
        if limit is None:
            return True
        active_claimers = ACCoordinator._active_claimers(competition)
        if arenaclient.id in active_claimers[:limit]:
            return True
        return len(active_claimers) < limit

    @staticmethod
    def _active_claimers(competition: Competition) -> list[int]:
        """Arena clients currently active in a competition's ladder, in claim order.

        Requested matches are not counted. A client is active while it holds an unfinished ladder
        match here, or finished one inside the match timeout. Matches cancelled by the timeout
        don't count, so a crashed client frees its slot as soon as its match is timed out. Only
        matches inside this window are read, so the query doesn't grow with competition history.
        """
        cutoff = timezone.now() - config.TIMEOUT_MATCHES_AFTER
        return list(
            Match.objects.filter(
                Q(result__isnull=True) | (Q(result__created__gte=cutoff) & ~Q(result__type="MatchCancelled")),
                round__competition=competition,
                requested_by__isnull=True,
                assigned_to__isnull=False,
                started__isnull=False,
            )
            .values("assigned_to_id")
            .annotate(first_started=Min("started"))
            .order_by("first_started", "assigned_to_id")
            .values_list("assigned_to_id", flat=True)
        )

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
