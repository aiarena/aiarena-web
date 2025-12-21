from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count

from aiarena.core.services.internal.rounds import update_round_if_completed


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from aiarena.core.models import Competition, Round

from aiarena.core.models import Bot, CompetitionParticipation


class Competitions:
    def get_active_bots(self, competition: Competition) -> QuerySet:
        return Bot.objects.only("id").filter(
            competition_participations__competition=competition, competition_participations__active=True
        )

    def get_active_participants(self, competition: Competition) -> QuerySet:
        return CompetitionParticipation.objects.only("id").filter(competition=competition, active=True)

    def check_has_matches_to_play_and_apply_locks(self, competition: Competition) -> bool:
        """This checks that there are matches to be played for the specified competition and also applies any
        relevant database locks"""
        # todo: add check for whether new rounds can be generated here
        return self.get_active_participants(competition).select_for_update().count() >= 2

    def has_reached_maximum_active_rounds(self, competition: Competition):
        return competition.round_set.filter(complete=False).count() >= competition.max_active_rounds

    def bot_type_stats(self, competition: Competition):
        type_to_participant_count = {
            competition["bot__type"]: competition["total"]
            for competition in competition.participations.values("bot__type").annotate(total=Count("bot__type"))
        }
        for _, bot_type in Bot.TYPES:
            type_to_participant_count.setdefault(bot_type, 0)
        return type_to_participant_count

    def disable_bot_for_all_competitions(self, bot) -> int:
        """Disables a bot for all its active competition participations."""
        participations = CompetitionParticipation.objects.filter(bot=bot, active=True)
        updated = participations.update(active=False)
        return updated

    def update_competition_round_if_completed(self, round: Round):
        update_round_if_completed(round)
