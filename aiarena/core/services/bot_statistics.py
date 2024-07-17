from django.db.models import Exists, Max, OuterRef, Q

from django_pglocks import advisory_lock

from aiarena.core.models import CompetitionParticipation, Map, Match, MatchParticipation, Result
from aiarena.core.models.competition_bot_map_stats import CompetitionBotMapStats
from aiarena.core.models.competition_bot_matchup_stats import CompetitionBotMatchupStats
from aiarena.core.services.internal.statistics.elo_graphs_generator import EloGraphsGenerator


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

    def __init__(self, competition_participation: CompetitionParticipation):
        self.participation = competition_participation

    def update_stats_based_on_result(self, result: Result, opponent_participation: CompetitionParticipation):
        """This method updates a bot's existing stats based on a single result.
        This can be done much quicker that regenerating a bot's entire set of stats"""

        if (
            result.type not in self._ignored_result_types
            and self.participation.competition.indepth_bot_statistics_enabled
        ):
            with advisory_lock(f"stats_lock_competitionparticipation_{self.participation.id}") as acquired:
                if not acquired:
                    raise Exception(
                        "Could not acquire lock on bot statistics for competition participation "
                        + str(self.participation.id)
                    )
                self._update_global_statistics(result)
                self._update_matchup_stats(opponent_participation, result)
                self._update_map_stats(result)

    def recalculate_stats(self):
        """This method entirely recalculates a bot's set of stats."""

        with advisory_lock(f"stats_lock_competitionparticipation_{self.participation.id}") as acquired:
            if not acquired:
                raise Exception(
                    f"Could not acquire lock on bot statistics for competition participation  {str(self.participation.id)}"
                )

            self._recalculate_global_statistics()

            if self.participation.competition.indepth_bot_statistics_enabled:
                self._recalculate_matchup_stats()
                self._recalculate_map_stats()

    def _recalculate_global_statistics(self):
        self.participation.match_count = (
            MatchParticipation.objects.filter(
                bot=self.participation.bot,
                match__result__isnull=False,
                match__round__competition=self.participation.competition,
            )
            .exclude(match__result__type__in=self._ignored_result_types)
            .count()
        )
        if self.participation.match_count != 0:
            self.participation.win_count = MatchParticipation.objects.filter(
                self.result_win, bot=self.participation.bot, match__round__competition=self.participation.competition
            ).count()
            self.participation.win_perc = self.participation.win_count / self.participation.match_count * 100

            if self.participation.competition.indepth_bot_statistics_enabled:
                self.participation.loss_count = MatchParticipation.objects.filter(
                    self.result_loss,
                    bot=self.participation.bot,
                    match__round__competition=self.participation.competition,
                ).count()
                self.participation.loss_perc = self.participation.loss_count / self.participation.match_count * 100
                self.participation.tie_count = MatchParticipation.objects.filter(
                    self.result_tie,
                    bot=self.participation.bot,
                    match__round__competition=self.participation.competition,
                ).count()
                self.participation.tie_perc = self.participation.tie_count / self.participation.match_count * 100
                self.participation.crash_count = MatchParticipation.objects.filter(
                    self.result_crash,
                    bot=self.participation.bot,
                    match__round__competition=self.participation.competition,
                ).count()
                self.participation.crash_perc = self.participation.crash_count / self.participation.match_count * 100

                self.participation.highest_elo = (
                    MatchParticipation.objects.filter(
                        bot=self.participation.bot,
                        match__result__isnull=False,
                        match__round__competition=self.participation.competition,
                    )
                    .exclude(match__result__type__in=self._ignored_result_types)
                    .aggregate(Max("resultant_elo"))["resultant_elo__max"]
                )
                self.generate_graphs()
        self.participation.save()

    def generate_graphs(self):
        graph1, graph2, graph3 = EloGraphsGenerator(self.participation).generate()
        if graph1 is not None:
            self.participation.elo_graph.save("elo.png", graph1, False)
        if graph2 is not None:
            self.participation.elo_graph_update_plot.save("elo_update_plot.png", graph2, False)
        if graph3 is not None:
            self.participation.winrate_vs_duration_graph.save("winrate_vs_duration.png", graph3, False)

    def _update_global_statistics(self, result: Result):
        self.participation.match_count += 1

        if result.has_winner:
            if self.participation.bot == result.winner:
                self.participation.win_count += 1
                if self.participation.highest_elo is None or self.participation.highest_elo < self.participation.elo:
                    self.participation.highest_elo = self.participation.elo
            else:
                self.participation.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=self.participation.bot).crashed:
                    self.participation.crash_count += 1

                # self.participationecial case to match a full recalc:
                # Set highest_elo isn't already - this will only trigger on a loss or tie
                # This is easier than changing the way the full recalc determines this figure
                if self.participation.highest_elo is None:
                    self.participation.highest_elo = self.participation.elo

        elif result.is_tie:
            self.participation.tie_count += 1

            # self.participationecial case to match a full recalc:
            # Set highest_elo isn't already - this will only trigger on a loss or tie
            # This is easier than changing the way the full recalc determines this figure
            if self.participation.highest_elo is None:
                self.participation.highest_elo = self.participation.elo
        else:
            raise Exception("Unexpected result type: %s", result.type)

        self.participation.win_perc = self.participation.win_count / self.participation.match_count * 100
        self.participation.loss_perc = self.participation.loss_count / self.participation.match_count * 100
        self.participation.tie_perc = self.participation.tie_count / self.participation.match_count * 100
        self.participation.crash_perc = self.participation.crash_count / self.participation.match_count * 100

        # TODO: implement caching so that this runs quick enough to include in this job
        # BotStatistics._generate_graphs(self.participation)

        self.participation.save()

    def _recalculate_matchup_stats(self):
        CompetitionBotMatchupStats.objects.filter(bot=self.participation).delete()

        for opponent_p in CompetitionParticipation.objects.filter(competition=self.participation.competition).exclude(
            bot=self.participation.bot
        ):
            match_count = self._calculate_matchup_data(opponent_p, self.result_exists)
            if not match_count:
                continue

            matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(
                bot=self.participation, opponent=opponent_p
            )[0]
            matchup_stats.match_count = match_count

            matchup_stats.win_count = self._calculate_matchup_data(opponent_p, self.result_win)
            matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100

            matchup_stats.loss_count = self._calculate_matchup_data(opponent_p, self.result_loss)
            matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100

            matchup_stats.tie_count = self._calculate_matchup_data(opponent_p, self.result_tie)
            matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100

            matchup_stats.crash_count = self._calculate_matchup_data(opponent_p, self.result_crash)
            matchup_stats.crash_perc = matchup_stats.crash_count / matchup_stats.match_count * 100

            matchup_stats.save()

    def _update_matchup_stats(self, opponent: CompetitionParticipation, result: Result):
        matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(bot=self.participation, opponent=opponent)[0]

        matchup_stats.match_count += 1

        if result.has_winner:
            if self.participation.bot == result.winner:
                matchup_stats.win_count += 1
            else:
                matchup_stats.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=self.participation.bot).crashed:
                    matchup_stats.crash_count += 1
        elif result.is_tie:
            matchup_stats.tie_count += 1
        else:
            raise Exception("Unexpected result type: %s", result.type)

        matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100
        matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100
        matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100
        matchup_stats.crash_perc = matchup_stats.crash_count / matchup_stats.match_count * 100

        matchup_stats.save()

    def _recalculate_map_stats(self):
        competition_matches = Match.objects.filter(
            round__competition_id=self.participation.competition.id
        ).select_related("map")
        maps = Map.objects.filter(id__in=competition_matches.values_list("map_id", flat=True))

        # purge existing stats entries for all maps
        CompetitionBotMapStats.objects.filter(bot=self.participation).delete()

        for map in maps:
            match_count = self._calculate_map_data(map, self.result_exists)
            if not match_count:
                continue

            map_stats = CompetitionBotMapStats.objects.create(bot=self.participation, map=map)
            map_stats.match_count = match_count

            map_stats.win_count = self._calculate_map_data(map, self.result_win)
            map_stats.win_perc = map_stats.win_count / map_stats.match_count * 100

            map_stats.loss_count = self._calculate_map_data(map, self.result_loss)
            map_stats.loss_perc = map_stats.loss_count / map_stats.match_count * 100

            map_stats.tie_count = self._calculate_map_data(map, self.result_tie)
            map_stats.tie_perc = map_stats.tie_count / map_stats.match_count * 100

            map_stats.crash_count = self._calculate_map_data(map, self.result_crash)
            map_stats.crash_perc = map_stats.crash_count / map_stats.match_count * 100

            map_stats.save()

    def _update_map_stats(self, result: Result):
        map_stats = CompetitionBotMapStats.objects.get_or_create(bot=self.participation, map=result.match.map)[0]
        map_stats.match_count += 1

        if result.has_winner:
            if self.participation.bot == result.winner:
                map_stats.win_count += 1
            else:
                map_stats.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=self.participation.bot).crashed:
                    map_stats.crash_count += 1
        elif result.is_tie:
            map_stats.tie_count += 1
        else:
            raise Exception("Unexpected result type: %s", result.type)

        map_stats.win_perc = map_stats.win_count / map_stats.match_count * 100
        map_stats.loss_perc = map_stats.loss_count / map_stats.match_count * 100
        map_stats.tie_perc = map_stats.tie_count / map_stats.match_count * 100
        map_stats.crash_perc = map_stats.crash_count / map_stats.match_count * 100

        map_stats.save()

    def _calculate_matchup_data(self, opponent_p, result_query):
        return Match.objects.filter(
            Exists(
                MatchParticipation.objects.filter(
                    result_query, match_id=OuterRef("id"), bot_id=self.participation.bot_id
                )
            ),
            Exists(MatchParticipation.objects.filter(match_id=OuterRef("id"), bot_id=opponent_p.bot_id)),
            round__competition=self.participation.competition_id,
        ).count()

    def _calculate_map_data(self, map, result_query):
        return Match.objects.filter(
            Exists(
                MatchParticipation.objects.filter(
                    result_query, match_id=OuterRef("id"), bot_id=self.participation.bot_id
                )
            ),
            map_id=map.id,
            round__competition=self.participation.competition_id,
        ).count()
