from django.db import connection
from django.db.models import Max

from django_pglocks import advisory_lock

from aiarena.core.models import CompetitionParticipation, Map, Match, MatchParticipation, Result
from aiarena.core.models.competition_bot_map_stats import CompetitionBotMapStats
from aiarena.core.models.competition_bot_matchup_stats import CompetitionBotMatchupStats
from aiarena.core.services.internal.statistics.elo_graphs_generator import EloGraphsGenerator


class BotStatistics:
    @staticmethod
    def update_stats_based_on_result(bot: CompetitionParticipation, result: Result, opponent: CompetitionParticipation):
        """This method updates a bot's existing stats based on a single result.
        This can be done much quicker that regenerating a bot's entire set of stats"""

        if result.type not in BotStatistics._ignored_result_types and bot.competition.indepth_bot_statistics_enabled:
            with advisory_lock(f"stats_lock_competitionparticipation_{bot.id}") as acquired:
                if not acquired:
                    raise Exception(
                        "Could not acquire lock on bot statistics for competition participation " + str(bot.id)
                    )
                BotStatistics._update_global_statistics(bot, result)
                BotStatistics._update_matchup_stats(bot, opponent, result)
                BotStatistics._update_map_stats(bot, result)

    @staticmethod
    def recalculate_stats(sp: CompetitionParticipation):
        """This method entirely recalculates a bot's set of stats."""

        with advisory_lock(f"stats_lock_competitionparticipation_{sp.id}") as acquired:
            if not acquired:
                raise Exception(f"Could not acquire lock on bot statistics for competition participation  {str(sp.id)}")

            BotStatistics._recalculate_global_statistics(sp)

            if sp.competition.indepth_bot_statistics_enabled:
                BotStatistics._recalculate_matchup_stats(sp)
                BotStatistics._recalculate_map_stats(sp)

    # ignore these result types for the purpose of statistics generation
    _ignored_result_types = ["MatchCancelled", "InitializationError", "Error"]

    @staticmethod
    def _recalculate_global_statistics(sp: CompetitionParticipation):
        sp.match_count = (
            MatchParticipation.objects.filter(
                bot=sp.bot, match__result__isnull=False, match__round__competition=sp.competition
            )
            .exclude(match__result__type__in=BotStatistics._ignored_result_types)
            .count()
        )
        if sp.match_count != 0:
            sp.win_count = MatchParticipation.objects.filter(
                bot=sp.bot, result="win", match__round__competition=sp.competition
            ).count()
            sp.win_perc = sp.win_count / sp.match_count * 100

            if sp.competition.indepth_bot_statistics_enabled:
                sp.loss_count = MatchParticipation.objects.filter(
                    bot=sp.bot, result="loss", match__round__competition=sp.competition
                ).count()
                sp.loss_perc = sp.loss_count / sp.match_count * 100
                sp.tie_count = MatchParticipation.objects.filter(
                    bot=sp.bot, result="tie", match__round__competition=sp.competition
                ).count()
                sp.tie_perc = sp.tie_count / sp.match_count * 100
                sp.crash_count = MatchParticipation.objects.filter(
                    bot=sp.bot,
                    result="loss",
                    result_cause__in=["crash", "timeout", "initialization_failure"],
                    match__round__competition=sp.competition,
                ).count()
                sp.crash_perc = sp.crash_count / sp.match_count * 100

                sp.highest_elo = (
                    MatchParticipation.objects.filter(
                        bot=sp.bot, match__result__isnull=False, match__round__competition=sp.competition
                    )
                    .exclude(match__result__type__in=BotStatistics._ignored_result_types)
                    .aggregate(Max("resultant_elo"))["resultant_elo__max"]
                )
                BotStatistics.generate_graphs(sp)
        sp.save()

    @staticmethod
    def generate_graphs(sp: CompetitionParticipation):
        graph1, graph2, graph3 = EloGraphsGenerator(sp).generate()
        if graph1 is not None:
            sp.elo_graph.save("elo.png", graph1, False)
        if graph2 is not None:
            sp.elo_graph_update_plot.save("elo_update_plot.png", graph2, False)
        if graph3 is not None:
            sp.winrate_vs_duration_graph.save("winrate_vs_duration.png", graph3, False)

    @staticmethod
    def _update_global_statistics(sp: CompetitionParticipation, result: Result):
        sp.match_count += 1

        if result.has_winner:
            if sp.bot == result.winner:
                sp.win_count += 1
                if sp.highest_elo is None or sp.highest_elo < sp.elo:
                    sp.highest_elo = sp.elo
            else:
                sp.loss_count += 1

                if MatchParticipation.objects.get(match=result.match, bot=sp.bot).crashed:
                    sp.crash_count += 1

                # Special case to match a full recalc:
                # Set highest_elo isn't already - this will only trigger on a loss or tie
                # This is easier than changing the way the full recalc determines this figure
                if sp.highest_elo is None:
                    sp.highest_elo = sp.elo

        elif result.is_tie:
            sp.tie_count += 1

            # Special case to match a full recalc:
            # Set highest_elo isn't already - this will only trigger on a loss or tie
            # This is easier than changing the way the full recalc determines this figure
            if sp.highest_elo is None:
                sp.highest_elo = sp.elo
        else:
            raise Exception("Unexpected result type: %s", result.type)

        sp.win_perc = sp.win_count / sp.match_count * 100
        sp.loss_perc = sp.loss_count / sp.match_count * 100
        sp.tie_perc = sp.tie_count / sp.match_count * 100
        sp.crash_perc = sp.crash_count / sp.match_count * 100

        # TODO: implement caching so that this runs quick enough to include in this job
        # BotStatistics._generate_graphs(sp)

        sp.save()

    @staticmethod
    def _recalculate_matchup_stats(sp: CompetitionParticipation):
        CompetitionBotMatchupStats.objects.filter(bot=sp).delete()

        for competition_participation in CompetitionParticipation.objects.filter(competition=sp.competition).exclude(
            bot=sp.bot
        ):
            with connection.cursor() as cursor:
                match_count = BotStatistics._calculate_matchup_count(cursor, competition_participation, sp)
                if match_count > 0:
                    matchup_stats = CompetitionBotMatchupStats.objects.get_or_create(
                        bot=sp, opponent=competition_participation
                    )[0]

                    matchup_stats.match_count = match_count
                    matchup_stats.win_count = BotStatistics._calculate_matchup_win_count(
                        cursor, competition_participation, sp
                    )
                    matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100

                    matchup_stats.loss_count = BotStatistics._calculate_matchup_loss_count(
                        cursor, competition_participation, sp
                    )
                    matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100

                    matchup_stats.tie_count = BotStatistics._calculate_matchup_tie_count(
                        cursor, competition_participation, sp
                    )
                    matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100

                    matchup_stats.crash_count = BotStatistics._calculate_matchup_crash_count(
                        cursor, competition_participation, sp
                    )
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

    @staticmethod
    def _recalculate_map_stats(sp: CompetitionParticipation):
        competition_matches = Match.objects.filter(round__competition_id=sp.competition.id).select_related("map")
        maps = Map.objects.filter(id__in=competition_matches.values_list("map_id", flat=True))

        # purge existing stats entries for all maps
        CompetitionBotMapStats.objects.filter(bot=sp).delete()

        for map in maps:
            with connection.cursor() as cursor:
                match_count = BotStatistics._calculate_map_count(cursor, map, sp)
                if match_count > 0:
                    map_stats = CompetitionBotMapStats.objects.create(bot=sp, map=map)
                    map_stats.match_count = match_count

                    map_stats.win_count = BotStatistics._calculate_map_win_count(cursor, map, sp)
                    map_stats.win_perc = map_stats.win_count / map_stats.match_count * 100

                    map_stats.loss_count = BotStatistics._calculate_map_loss_count(cursor, map, sp)
                    map_stats.loss_perc = map_stats.loss_count / map_stats.match_count * 100

                    map_stats.tie_count = BotStatistics._calculate_map_tie_count(cursor, map, sp)
                    map_stats.tie_perc = map_stats.tie_count / map_stats.match_count * 100

                    map_stats.crash_count = BotStatistics._calculate_map_crash_count(cursor, map, sp)
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
    def _run_single_column_query(cursor, query, params):
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0]

    @staticmethod
    def _calculate_matchup_data(cursor, competition_participation, sp, query):
        return BotStatistics._run_single_column_query(
            cursor,
            """
                    select count(cm.id) as count
                    from core_match cm
                    inner join core_matchparticipation bot_p on cm.id = bot_p.match_id
                    inner join core_matchparticipation opponent_p on cm.id = opponent_p.match_id
                    inner join core_round cr on cm.round_id = cr.id
                    inner join core_competition cs on cr.competition_id = cs.id
                    where cs.id = %s -- make sure it's part of the current competition
                    and bot_p.bot_id = %s
                    and opponent_p.bot_id = %s
                    and """
            + query,
            [sp.competition_id, sp.bot_id, competition_participation.bot_id],
        )

    @staticmethod
    def _calculate_matchup_count(cursor, competition_participation, sp):
        return BotStatistics._calculate_matchup_data(
            cursor, competition_participation, sp, "bot_p.result is not null and bot_p.result != 'none'"
        )

    @staticmethod
    def _calculate_matchup_win_count(cursor, competition_participation, sp):
        return BotStatistics._calculate_matchup_data(cursor, competition_participation, sp, "bot_p.result = 'win'")

    @staticmethod
    def _calculate_matchup_loss_count(cursor, competition_participation, sp):
        return BotStatistics._calculate_matchup_data(cursor, competition_participation, sp, "bot_p.result = 'loss'")

    @staticmethod
    def _calculate_matchup_tie_count(cursor, competition_participation, sp):
        return BotStatistics._calculate_matchup_data(cursor, competition_participation, sp, "bot_p.result = 'tie'")

    @staticmethod
    def _calculate_matchup_crash_count(cursor, competition_participation, sp):
        return BotStatistics._calculate_matchup_data(
            cursor,
            competition_participation,
            sp,
            """bot_p.result = 'loss'
                                                     and bot_p.result_cause in ('crash', 'timeout', 'initialization_failure')""",
        )

    @staticmethod
    def _calculate_map_data(cursor, map, sp, query):
        return BotStatistics._run_single_column_query(
            cursor,
            """
                    select count(cm.id) as count
                    from core_match cm
                    inner join core_matchparticipation bot_p on cm.id = bot_p.match_id
                    inner join core_map map on cm.map_id = map.id
                    inner join core_round cr on cm.round_id = cr.id
                    inner join core_competition cs on cr.competition_id = cs.id
                    where cs.id = %s -- make sure it's part of the current competition
                    and map.id = %s
                    and bot_p.bot_id = %s
                    and """
            + query,
            [sp.competition_id, map.id, sp.bot_id],
        )

    @staticmethod
    def _calculate_map_count(cursor, map, sp):
        return BotStatistics._calculate_map_data(cursor, map, sp, "bot_p.result is not null and bot_p.result != 'none'")

    @staticmethod
    def _calculate_map_win_count(cursor, map, sp):
        return BotStatistics._calculate_map_data(cursor, map, sp, "bot_p.result = 'win'")

    @staticmethod
    def _calculate_map_loss_count(cursor, map, sp):
        return BotStatistics._calculate_map_data(cursor, map, sp, "bot_p.result = 'loss'")

    @staticmethod
    def _calculate_map_tie_count(cursor, map, sp):
        return BotStatistics._calculate_map_data(cursor, map, sp, "bot_p.result = 'tie'")

    @staticmethod
    def _calculate_map_crash_count(cursor, map, sp):
        return BotStatistics._calculate_map_data(
            cursor,
            map,
            sp,
            """bot_p.result = 'loss'
                                                 and bot_p.result_cause in ('crash', 'timeout', 'initialization_failure')""",
        )
