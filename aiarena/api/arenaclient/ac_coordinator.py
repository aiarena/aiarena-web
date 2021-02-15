from __future__ import annotations

from typing import TYPE_CHECKING

from aiarena.core.api.competitions import Competitions

if TYPE_CHECKING:
    from aiarena.core.models import ArenaClient

import logging

from constance import config
from django.db import transaction, connection
from django.db.models import F

from aiarena.api.arenaclient.exceptions import LadderDisabled, NoCurrentlyAvailableCompetitions
from aiarena.core.api import Matches
from aiarena.core.models import Match, Competition

logger = logging.getLogger(__name__)


class ACCoordinator:
    """Coordinates all the Arena Clients and which matches they play."""

    @staticmethod
    def next_competition_match(arenaclient: ArenaClient):
        # REQUESTED MATCHES
        with transaction.atomic():
            match = Matches.attempt_to_start_a_requested_match(arenaclient)
            if match is not None:
                return match  # a match was found - we're done

        competition_ids = ACCoordinator._get_competition_priority_order()
        for id in competition_ids:
            competition = Competition.objects.get(id=id)
            # this atomic block is done inside the for loop so that we don't hold onto a lock for a single competition
            with transaction.atomic():
                # this call will apply a select for update, so we do it inside an atomic block
                if Competitions.check_has_matches_to_play_and_apply_locks(competition):
                    return Matches.start_next_match_for_competition(arenaclient, competition)

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

    @staticmethod
    def _get_competition_priority_order():
        """
        Returns a list of competition ids in priority order with respect to the current number of active participants
         in each competition verses each competition's share of the most recent 100 matches.
         In otherwords, campetitions with higher active participant counts should play more matches overall.
        :return:
        """
        with connection.cursor() as cursor:
            # I don't know why but for some reason CTEs didn't work so here; have a massive query.
            cursor.execute("""
                select perc_active.competition_id
                from (select competition_id, competition_participations.competition_participations_cnt / total_active_cnt as perc_active
                      from (select cp.competition_id, count(cp.competition_id) competition_participations_cnt
                            from core_competitionparticipation cp
                                     join core_competition cc on cp.competition_id = cc.id
                            where cp.active = 1
                              and cc.status in ('open', 'closing', 'paused')
                            group by cp.competition_id) as competition_participations
                               join
                           (select count(*) total_active_cnt
                            from core_competitionparticipation cp
                                     join core_competition cc on cp.competition_id = cc.id
                            where cp.active = 1
                              and cc.status in ('open', 'closing', 'paused')) as competition_participations_total) as perc_active
                         left join
                     (select competition_id, perc_recent_matches_cnt / total_matches_cnt as perc_recent_matches
                      from (select competition_id, count(competition_id) perc_recent_matches_cnt, count(*) total_matches_cnt
                            from (select competition_id
                                  from core_match cm
                                           join core_round cr on cm.round_id = cr.id
                                           join core_competition cc on cr.competition_id = cc.id
                                  where cm.started is not null
                                    and cc.status in ('open', 'closing', 'paused')
                                  order by cm.started desc
                                  limit 100) as matches
                            group by competition_id) as recent_matches) as perc_recent_matches
                     on perc_recent_matches.competition_id = perc_active.competition_id
                order by COALESCE(perc_recent_matches, 0) - perc_active
            """)
            return [row[0] for row in cursor.fetchall()]  # return competition ids
