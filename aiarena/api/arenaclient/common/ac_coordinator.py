from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.dispatch import receiver

from aiarena.core.services import competitions


if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from django.db import connection, transaction
from django.db.models.signals import pre_save

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
        for id in competition_ids:
            competition = Competition.objects.get(id=id)
            # This excludes non-trusted clients from competitions requiring trusted infrastructure
            if arenaclient.trusted or competition.require_trusted_infrastructure == arenaclient.trusted:
                # this atomic block is done inside the for loop so that we don't hold onto a lock for a single competition
                with transaction.atomic():
                    # this call will apply a select for update, so we do it inside an atomic block
                    if competitions.check_has_matches_to_play_and_apply_locks(competition):
                        try:
                            return matches.start_next_match_for_competition(arenaclient, competition)
                        except (
                            NoMaps,
                            NotEnoughAvailableBots,
                            MaxActiveRounds,
                            CompetitionPaused,
                            CompetitionClosing,
                        ) as e:
                            logger.debug(f"Skipping competition {id}: {e}")
                            continue

        return None

    @staticmethod
    def next_new_match(arenaclient: ArenaClient):
        requested_match = ACCoordinator.next_requested_match(arenaclient)
        if requested_match is not None:
            return requested_match
        return ACCoordinator.next_competition_match(arenaclient)

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
