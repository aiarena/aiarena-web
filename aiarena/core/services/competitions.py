from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from aiarena.core.models import Competition

from aiarena.core.models import Bot, CompetitionParticipation


class Competitions:
    @staticmethod
    def get_active_bots(competition: Competition) -> QuerySet:
        return Bot.objects.only("id").filter(
            competition_participations__competition=competition, competition_participations__active=True
        )

    @staticmethod
    def get_active_participants(competition: Competition) -> QuerySet:
        return CompetitionParticipation.objects.only("id").filter(competition=competition, active=True)

    @staticmethod
    def check_has_matches_to_play_and_apply_locks(competition: Competition) -> bool:
        """This checks that there are matches to be played for the specified competition and also applies any
        relevant database locks"""
        # todo: add check for whether new rounds can be generated here
        return Competitions.get_active_participants(competition).select_for_update().count() >= 2

    @staticmethod
    def has_reached_maximum_active_rounds(competition: Competition):
        return competition.round_set.filter(complete=False).count() >= competition.max_active_rounds

    @staticmethod
    def bot_type_stats(competition: Competition):
        type_to_participant_count = {
            competition["bot__type"]: competition["total"]
            for competition in competition.participations.values("bot__type").annotate(total=Count("bot__type"))
        }
        for _, bot_type in Bot.TYPES:
            type_to_participant_count.setdefault(bot_type, 0)
        return type_to_participant_count
