from django.db.models import Exists, Max, OuterRef, Q

import sentry_sdk
from django_pglocks import advisory_lock

from aiarena.core.models import CompetitionParticipation, Map, Match, MatchParticipation, Result
from aiarena.core.models.competition_bot_map_stats import CompetitionBotMapStats
from aiarena.core.models.competition_bot_matchup_stats import CompetitionBotMatchupStats

from .internal.statistics.elo_graphs_generator import EloGraphsGenerator


class BotStatistics:
    result_exists = ~Q(result=None) & ~Q(result="none")
    result_win = Q(result="win")
    result_loss = Q(result="loss")
    result_tie = Q(result="tie")
    result_crash = Q(
        result="loss",
        result_cause__in=["crash", "timeout", "initialization_failure"],
    )

    # ignore these result types for the purpose of statistics generation
    _ignored_result_types = ["MatchCancelled", "InitializationError", "Error"]

    def update_stats_based_on_result(
        self,
        competition_participation: CompetitionParticipation,
        result: Result,
        opponent_participation: CompetitionParticipation,
    ):
        """This method updates a bot's existing stats based on a single result.
        This can be done much quicker that regenerating a bot's entire set of stats"""

        if (
            result.type not in self._ignored_result_types
            and competition_participation.competition.indepth_bot_statistics_enabled
        ):
            with advisory_lock(f"stats_lock_competitionparticipation_{competition_participation.id}") as acquired:
                if not acquired:
                    raise Exception(
                        "Could not acquire lock on bot statistics for competition participation "
                        + str(competition_participation.id)
                    )
                self._update_global_statistics(competition_participation, result)
                self._update_matchup_stats(competition_participation, opponent_participation, result)
                self._update_map_stats(competition_participation, result)

    def recalculate_stats(self, competition_participation: CompetitionParticipation):
        """This method entirely recalculates a bot's set of stats."""

        with advisory_lock(f"stats_lock_competitionparticipation_{competition_participation.id}") as acquired:
            if not acquired:
                raise Exception(
                    f"Could not acquire lock on bot statistics for competition participation  {str(competition_participation.id)}"
                )

            self._recalculate_global_statistics(competition_participation)

            if competition_participation.competition.indepth_bot_statistics_enabled:
                self._recalculate_matchup_stats(competition_participation)
                self._recalculate_map_stats(competition_participation)

    def _recalculate_global_statistics(self, participation: CompetitionParticipation):
        participation.match_count = (
            MatchParticipation.objects.filter(
                bot=participation.bot,
                match__result__isnull=False,
                match__round__competition=participation.competition,
            )
            .exclude(match__result__type__in=self._ignored_result_types)
            .count()
        )
        if participation.match_count != 0:
            participation.win_count = MatchParticipation.objects.filter(
                self.result_win, bot=participation.bot, match__round__competition=participation.competition
            ).count()
            participation.win_perc = participation.win_count / participation.match_count * 100

            if participation.competition.indepth_bot_statistics_enabled:
                participation.loss_count = MatchParticipation.objects.filter(
                    self.result_loss,
                    bot=participation.bot,
                    match__round__competition=participation.competition,
                ).count()
                participation.loss_perc = participation.loss_count / participation.match_count * 100
                participation.tie_count = MatchParticipation.objects.filter(
                    self.result_tie,
                    bot=participation.bot,
                    match__round__competition=participation.competition,
                ).count()
                participation.tie_perc = participation.tie_count / participation.match_count * 100
                participation.crash_count = MatchParticipation.objects.filter(
                    self.result_crash,
                    bot=participation.bot,
                    match__round__competition=participation.competition,
                ).count()
                participation.crash_perc = participation.crash_count / participation.match_count * 100

                participation.highest_elo = (
                    MatchParticipation.objects.filter(
                        bot=participation.bot,
                        match__result__isnull=False,
                        match__round__competition=participation.competition,
                    )
                    .exclude(match__result__type__in=self._ignored_result_types)
                    .aggregate(Max("resultant_elo"))["resultant_elo__max"]
                )
                self.generate_graphs(participation)
        participation.save()

    def generate_graphs(self, participation: CompetitionParticipation):
        graph1, graph2, graph3 = EloGraphsGenerator(participation).generate()
        if graph1 is not None:
            participation.elo_graph.save("elo.png", graph1, False)
        if graph2 is not None:
            participation.elo_graph_update_plot.save("elo_update_plot.png", graph2, False)
        if graph3 is not None:
            participation.winrate_vs_duration_graph.save("winrate_vs_duration.png", graph3, False)

    def _update_global_statistics(self, participation: CompetitionParticipation, result: Result):
        participation.match_count += 1

        if result.has_winner:
            if participation.bot == result.winner:
                participation.win_count += 1
                if participation.highest_elo is None or participation.highest_elo < participation.elo:
                    participation.highest_elo = participation.elo
            else:
                participation.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=participation.bot).crashed:
                    participation.crash_count += 1

                # Special case to match a full recalc:
                # Set highest_elo isn't already - this will only trigger on a loss or tie
                # This is easier than changing the way the full recalc determines this figure
                if participation.highest_elo is None:
                    participation.highest_elo = participation.elo

        elif result.is_tie:
            participation.tie_count += 1

            # Special case to match a full recalc:
            # Set highest_elo isn't already - this will only trigger on a loss or tie
            # This is easier than changing the way the full recalc determines this figure
            if participation.highest_elo is None:
                participation.highest_elo = participation.elo
        else:
            raise Exception("Unexpected result type: %s", result.type)

        participation.win_perc = participation.win_count / participation.match_count * 100
        participation.loss_perc = participation.loss_count / participation.match_count * 100
        participation.tie_perc = participation.tie_count / participation.match_count * 100
        participation.crash_perc = participation.crash_count / participation.match_count * 100

        # TODO: implement caching so that this runs quick enough to include in this job
        # BotStatistics._generate_graphs(self.participation)

        participation.save()

    def _recalculate_matchup_stats(self, participation: CompetitionParticipation):
        CompetitionBotMatchupStats.objects.filter(bot=participation).delete()

        for opponent_p in CompetitionParticipation.objects.filter(competition=participation.competition).exclude(
            bot=participation.bot
        ):
            match_count = self._calculate_matchup_data(participation, opponent_p, self.result_exists)
            if not match_count:
                continue

            matchup_stats, created = CompetitionBotMatchupStats.objects.get_or_create(
                bot=participation,
                opponent=opponent_p,
            )
            matchup_stats.match_count = match_count

            matchup_stats.win_count = self._calculate_matchup_data(participation, opponent_p, self.result_win)
            matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100

            matchup_stats.loss_count = self._calculate_matchup_data(participation, opponent_p, self.result_loss)
            matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100

            matchup_stats.tie_count = self._calculate_matchup_data(participation, opponent_p, self.result_tie)
            matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100

            matchup_stats.crash_count = self._calculate_matchup_data(participation, opponent_p, self.result_crash)
            matchup_stats.crash_perc = matchup_stats.crash_count / matchup_stats.match_count * 100

            if not created and matchup_stats.is_dirty():
                sentry_sdk.capture_message("Recalculated bot matchup stats differ from previous value")

            matchup_stats.save()

    def _recalculate_map_stats(self, participation: CompetitionParticipation):
        competition_matches = Match.objects.filter(round__competition_id=participation.competition.id).select_related(
            "map"
        )
        maps = Map.objects.filter(id__in=competition_matches.values_list("map_id", flat=True))

        for map in maps:
            match_count = self._calculate_map_data(participation, map, self.result_exists)
            if not match_count:
                continue

            map_stats, created = CompetitionBotMapStats.objects.get_or_create(bot=participation, map=map)
            map_stats.match_count = match_count

            map_stats.win_count = self._calculate_map_data(participation, map, self.result_win)
            map_stats.win_perc = map_stats.win_count / map_stats.match_count * 100

            map_stats.loss_count = self._calculate_map_data(participation, map, self.result_loss)
            map_stats.loss_perc = map_stats.loss_count / map_stats.match_count * 100

            map_stats.tie_count = self._calculate_map_data(participation, map, self.result_tie)
            map_stats.tie_perc = map_stats.tie_count / map_stats.match_count * 100

            map_stats.crash_count = self._calculate_map_data(participation, map, self.result_crash)
            map_stats.crash_perc = map_stats.crash_count / map_stats.match_count * 100

            if not created and map_stats.is_dirty():
                sentry_sdk.capture_message("Recalculated bot map stats differ from previous value")

            map_stats.save()

    def _update_matchup_stats(
        self,
        participation: CompetitionParticipation,
        opponent: CompetitionParticipation,
        result: Result,
    ):
        matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(bot=participation, opponent=opponent)[0]
        self._update_stats(participation, result, matchup_stats)

    def _update_map_stats(self, participation: CompetitionParticipation, result: Result):
        map_stats = CompetitionBotMapStats.objects.get_or_create(bot=participation, map=result.match.map)[0]
        self._update_stats(participation, result, map_stats)

    def _update_stats(self, participation: CompetitionParticipation, result: Result, stats):
        stats.match_count += 1

        if result.has_winner:
            if participation.bot == result.winner:
                stats.win_count += 1
            else:
                stats.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=participation.bot).crashed:
                    stats.crash_count += 1
        elif result.is_tie:
            stats.tie_count += 1
        else:
            raise Exception("Unexpected result type: %s", result.type)

        stats.win_perc = stats.win_count / stats.match_count * 100
        stats.loss_perc = stats.loss_count / stats.match_count * 100
        stats.tie_perc = stats.tie_count / stats.match_count * 100
        stats.crash_perc = stats.crash_count / stats.match_count * 100

        stats.save()

    def _calculate_matchup_data(self, participation: CompetitionParticipation, opponent_p, result_query):
        return Match.objects.filter(
            Exists(
                MatchParticipation.objects.filter(result_query, match_id=OuterRef("id"), bot_id=participation.bot_id)
            ),
            Exists(MatchParticipation.objects.filter(match_id=OuterRef("id"), bot_id=opponent_p.bot_id)),
            round__competition=participation.competition_id,
        ).count()

    def _calculate_map_data(self, participation: CompetitionParticipation, map, result_query):
        return Match.objects.filter(
            Exists(
                MatchParticipation.objects.filter(result_query, match_id=OuterRef("id"), bot_id=participation.bot_id)
            ),
            map_id=map.id,
            round__competition=participation.competition_id,
        ).count()
