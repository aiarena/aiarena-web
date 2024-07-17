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

    def update_stats_based_on_result(
        self, self_p: CompetitionParticipation, result: Result, opponent_p: CompetitionParticipation
    ):
        """This method updates a bot's existing stats based on a single result.
        This can be done much quicker that regenerating a bot's entire set of stats"""

        if result.type not in self._ignored_result_types and self_p.competition.indepth_bot_statistics_enabled:
            with advisory_lock(f"stats_lock_competitionparticipation_{self_p.id}") as acquired:
                if not acquired:
                    raise Exception(
                        "Could not acquire lock on bot statistics for competition participation " + str(self_p.id)
                    )
                self._update_global_statistics(self_p, result)
                self._update_matchup_stats(self_p, opponent_p, result)
                self._update_map_stats(self_p, result)

    def recalculate_stats(self, self_p: CompetitionParticipation):
        """This method entirely recalculates a bot's set of stats."""

        with advisory_lock(f"stats_lock_competitionparticipation_{self_p.id}") as acquired:
            if not acquired:
                raise Exception(
                    f"Could not acquire lock on bot statistics for competition participation  {str(self_p.id)}"
                )

            self._recalculate_global_statistics(self_p)

            if self_p.competition.indepth_bot_statistics_enabled:
                self._recalculate_matchup_stats(self_p)
                self._recalculate_map_stats(self_p)

    def _recalculate_global_statistics(self, self_p: CompetitionParticipation):
        self_p.match_count = (
            MatchParticipation.objects.filter(
                bot=self_p.bot, match__result__isnull=False, match__round__competition=self_p.competition
            )
            .exclude(match__result__type__in=self._ignored_result_types)
            .count()
        )
        if self_p.match_count != 0:
            self_p.win_count = MatchParticipation.objects.filter(
                self.result_win, bot=self_p.bot, match__round__competition=self_p.competition
            ).count()
            self_p.win_perc = self_p.win_count / self_p.match_count * 100

            if self_p.competition.indepth_bot_statistics_enabled:
                self_p.loss_count = MatchParticipation.objects.filter(
                    self.result_loss, bot=self_p.bot, match__round__competition=self_p.competition
                ).count()
                self_p.loss_perc = self_p.loss_count / self_p.match_count * 100
                self_p.tie_count = MatchParticipation.objects.filter(
                    self.result_tie, bot=self_p.bot, match__round__competition=self_p.competition
                ).count()
                self_p.tie_perc = self_p.tie_count / self_p.match_count * 100
                self_p.crash_count = MatchParticipation.objects.filter(
                    self.result_crash,
                    bot=self_p.bot,
                    match__round__competition=self_p.competition,
                ).count()
                self_p.crash_perc = self_p.crash_count / self_p.match_count * 100

                self_p.highest_elo = (
                    MatchParticipation.objects.filter(
                        bot=self_p.bot, match__result__isnull=False, match__round__competition=self_p.competition
                    )
                    .exclude(match__result__type__in=self._ignored_result_types)
                    .aggregate(Max("resultant_elo"))["resultant_elo__max"]
                )
                self.generate_graphs(self_p)
        self_p.save()

    @staticmethod
    def generate_graphs(self_p: CompetitionParticipation):
        graph1, graph2, graph3 = EloGraphsGenerator(self_p).generate()
        if graph1 is not None:
            self_p.elo_graph.save("elo.png", graph1, False)
        if graph2 is not None:
            self_p.elo_graph_update_plot.save("elo_update_plot.png", graph2, False)
        if graph3 is not None:
            self_p.winrate_vs_duration_graph.save("winrate_vs_duration.png", graph3, False)

    @staticmethod
    def _update_global_statistics(self_p: CompetitionParticipation, result: Result):
        self_p.match_count += 1

        if result.has_winner:
            if self_p.bot == result.winner:
                self_p.win_count += 1
                if self_p.highest_elo is None or self_p.highest_elo < self_p.elo:
                    self_p.highest_elo = self_p.elo
            else:
                self_p.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=self_p.bot).crashed:
                    self_p.crash_count += 1

                # self_pecial case to match a full recalc:
                # Set highest_elo isn't already - this will only trigger on a loss or tie
                # This is easier than changing the way the full recalc determines this figure
                if self_p.highest_elo is None:
                    self_p.highest_elo = self_p.elo

        elif result.is_tie:
            self_p.tie_count += 1

            # self_pecial case to match a full recalc:
            # Set highest_elo isn't already - this will only trigger on a loss or tie
            # This is easier than changing the way the full recalc determines this figure
            if self_p.highest_elo is None:
                self_p.highest_elo = self_p.elo
        else:
            raise Exception("Unexpected result type: %s", result.type)

        self_p.win_perc = self_p.win_count / self_p.match_count * 100
        self_p.loss_perc = self_p.loss_count / self_p.match_count * 100
        self_p.tie_perc = self_p.tie_count / self_p.match_count * 100
        self_p.crash_perc = self_p.crash_count / self_p.match_count * 100

        # TODO: implement caching so that this runs quick enough to include in this job
        # BotStatistics._generate_graphs(self_p)

        self_p.save()

    def _recalculate_matchup_stats(self, self_p: CompetitionParticipation):
        CompetitionBotMatchupStats.objects.filter(bot=self_p).delete()

        for opponent_p in CompetitionParticipation.objects.filter(competition=self_p.competition).exclude(
            bot=self_p.bot
        ):
            match_count = self._calculate_matchup_data(opponent_p, self_p, self.result_exists)
            if not match_count:
                continue

            matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(bot=self_p, opponent=opponent_p)[0]
            matchup_stats.match_count = match_count

            matchup_stats.win_count = self._calculate_matchup_data(opponent_p, self_p, self.result_win)
            matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100

            matchup_stats.loss_count = self._calculate_matchup_data(opponent_p, self_p, self.result_loss)
            matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100

            matchup_stats.tie_count = self._calculate_matchup_data(opponent_p, self_p, self.result_tie)
            matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100

            matchup_stats.crash_count = self._calculate_matchup_data(opponent_p, self_p, self.result_crash)
            matchup_stats.crash_perc = matchup_stats.crash_count / matchup_stats.match_count * 100

            matchup_stats.save()

    @staticmethod
    def _update_matchup_stats(bot: CompetitionParticipation, opponent: CompetitionParticipation, result: Result):
        matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(bot=bot, opponent=opponent)[0]

        matchup_stats.match_count += 1

        if result.has_winner:
            if bot.bot == result.winner:
                matchup_stats.win_count += 1
            else:
                matchup_stats.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=bot.bot).crashed:
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

    def _recalculate_map_stats(self, self_p: CompetitionParticipation):
        competition_matches = Match.objects.filter(round__competition_id=self_p.competition.id).select_related("map")
        maps = Map.objects.filter(id__in=competition_matches.values_list("map_id", flat=True))

        # purge existing stats entries for all maps
        CompetitionBotMapStats.objects.filter(bot=self_p).delete()

        for map in maps:
            match_count = self._calculate_map_data(map, self_p, self.result_exists)
            if not match_count:
                continue

            map_stats = CompetitionBotMapStats.objects.create(bot=self_p, map=map)
            map_stats.match_count = match_count

            map_stats.win_count = self._calculate_map_data(map, self_p, self.result_win)
            map_stats.win_perc = map_stats.win_count / map_stats.match_count * 100

            map_stats.loss_count = self._calculate_map_data(map, self_p, self.result_loss)
            map_stats.loss_perc = map_stats.loss_count / map_stats.match_count * 100

            map_stats.tie_count = self._calculate_map_data(map, self_p, self.result_tie)
            map_stats.tie_perc = map_stats.tie_count / map_stats.match_count * 100

            map_stats.crash_count = self._calculate_map_data(map, self_p, self.result_crash)
            map_stats.crash_perc = map_stats.crash_count / map_stats.match_count * 100

            map_stats.save()

    @staticmethod
    def _update_map_stats(bot: CompetitionParticipation, result: Result):
        map_stats = CompetitionBotMapStats.objects.get_or_create(bot=bot, map=result.match.map)[0]
        map_stats.match_count += 1

        if result.has_winner:
            if bot.bot == result.winner:
                map_stats.win_count += 1
            else:
                map_stats.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=bot.bot).crashed:
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

    @staticmethod
    def _calculate_matchup_data(opponent_p, self_p, result_query):
        return Match.objects.filter(
            Exists(MatchParticipation.objects.filter(result_query, match_id=OuterRef("id"), bot_id=self_p.bot_id)),
            Exists(MatchParticipation.objects.filter(match_id=OuterRef("id"), bot_id=opponent_p.bot_id)),
            round__competition=self_p.competition_id,
        )

    @staticmethod
    def _calculate_map_data(map, self_p, result_query):
        return Match.objects.filter(
            Exists(MatchParticipation.objects.filter(result_query, match_id=OuterRef("id"), bot_id=self_p.bot_id)),
            map_id=map.id,
            round__competition=self_p.competition_id,
        ).count()
