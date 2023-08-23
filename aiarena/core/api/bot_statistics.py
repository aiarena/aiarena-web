import io
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from django.db import connection
from django.db.models import Max
from django_pglocks import advisory_lock
from pytz import utc

from aiarena.core.models import MatchParticipation, CompetitionParticipation, Bot, Map, Match, Result
from aiarena.core.models.competition_bot_map_stats import CompetitionBotMapStats
from aiarena.core.models.competition_bot_matchup_stats import CompetitionBotMatchupStats


class BotStatistics:
    @staticmethod
    def update_stats_based_on_result(bot: CompetitionParticipation, result: Result, opponent: CompetitionParticipation):
        """This method updates a bot's existing stats based on a single result.
        This can be done much quicker that regenerating a bot's entire set of stats"""

        if result.type not in BotStatistics._ignored_result_types and bot.competition.indepth_bot_statistics_enabled:
            with advisory_lock(f"stats_lock_{bot.id}") as acquired:
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

        with advisory_lock(f"stats_lock_{sp.id}") as acquired:
            if not acquired:
                raise Exception("Could not acquire lock on bot statistics for competition participation " + str(sp.id))

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
                BotStatistics._generate_graphs(sp)
        sp.save()

    @staticmethod
    def _generate_graphs(sp):
        graph1, graph2 = BotStatistics._generate_elo_graph(sp.bot.id, sp.competition_id)
        if graph1 is not None:
            sp.elo_graph.save("elo.png", graph1)
        if graph2 is not None:
            sp.elo_graph_update_plot.save("elo_update_plot.png", graph2)
        graph3 = BotStatistics._generate_winrate_graph(sp.bot.id, sp.competition_id)
        if graph3 is not None:
            sp.winrate_vs_duration_graph.save("winrate_vs_duration.png", graph3)

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
            raise Exception(f"Unexpected result type: %s", result.type)

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
                    matchup_stats = CompetitionBotMatchupStats.objects.select_for_update().get_or_create(
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
        matchup_stats = CompetitionBotMatchupStats.objects.select_for_update().get_or_create(
            bot=bot, opponent=opponent
        )[0]

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
            raise Exception(f"Unexpected result type: %s", result.type)

        matchup_stats.win_perc = matchup_stats.win_count / matchup_stats.match_count * 100
        matchup_stats.loss_perc = matchup_stats.loss_count / matchup_stats.match_count * 100
        matchup_stats.tie_perc = matchup_stats.tie_count / matchup_stats.match_count * 100
        matchup_stats.crash_perc = matchup_stats.crash_count / matchup_stats.match_count * 100

        matchup_stats.save()

    @staticmethod
    def _recalculate_map_stats(sp: CompetitionParticipation):
        competition_matches = Match.objects.filter(round__competition_id=sp.competition.id)
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
            raise Exception(f"Unexpected result type: %s", result.type)

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

    @staticmethod
    def _get_elo_data(bot_id, competition_id):
        with connection.cursor() as cursor:
            query = f"""
                select 
                    cb.name, 
                    cp.resultant_elo as elo, 
                    cr.created as date
                from core_matchparticipation cp
                    inner join core_result cr on cp.match_id = cr.match_id
                    left join core_bot cb on cp.bot_id = cb.id
                    left join core_match cm on cp.match_id = cm.id
                    left join core_round crnd on cm.round_id = crnd.id
                    left join core_competition cc on crnd.competition_id = cc.id
                where resultant_elo is not null 
                    and bot_id = {bot_id} 
                    and competition_id = {competition_id}
                order by cr.created
                """
            cursor.execute(query)
            elo_over_time = pd.DataFrame(cursor.fetchall())

        earliest_result_datetime = BotStatistics.get_earliest_result_datetime(bot_id, competition_id)
        return elo_over_time, earliest_result_datetime

    @staticmethod
    def get_earliest_result_datetime(bot_id, competition_id):
        with connection.cursor() as cursor:
            query = f"""
                select 
                    MIN(cr.created) as date
                from core_matchparticipation cp
                    inner join core_result cr on cp.match_id = cr.match_id
                    left join core_bot cb on cp.bot_id = cb.id
                    left join core_match cm on cp.match_id = cm.id
                    left join core_round crnd on cm.round_id = crnd.id
                    left join core_competition cc on crnd.competition_id = cc.id
                where resultant_elo is not null 
                    and bot_id = {bot_id} 
                    and competition_id = {competition_id}
                """
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def _generate_elo_plot_images(df, update_date: datetime):
        plot1 = io.BytesIO()
        plot2 = io.BytesIO()

        legend = []

        fig, ax1 = plt.subplots(1, 1, figsize=(12, 9), sharex="all", sharey="all")
        ax1.plot(df["Date"], df["ELO"], color="#86c232")
        # ax.plot(df["Date"], df['ELO'], color='#86c232')
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["left"].set_color("#86c232")
        ax1.spines["bottom"].set_color("#86c232")
        ax1.autoscale(enable=True, axis="x")
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
        ax1.tick_params(axis="x", colors="#86c232", labelsize=16)
        ax1.tick_params(axis="y", colors="#86c232", labelsize=16)
        # if update_date:

        legend.append("ELO")
        ax1.legend(legend, loc="lower center", fontsize="xx-large")

        plt.title("ELO over time", fontsize=20, color=("#86c232"))
        plt.tight_layout()  # Avoids savefig cutting off x-label
        plt.savefig(plot1, format="png", transparent=True)

        ax1.vlines([update_date], min(df["ELO"]), max(df["ELO"]), colors="r", linestyles="--")
        legend.append("Last bot update")
        ax1.legend(legend, loc="lower center", fontsize="xx-large")
        plt.savefig(plot2, format="png", transparent=True)
        plt.close(fig)
        return plot1, plot2

    @staticmethod
    def _generate_elo_graph(bot_id: int, competition_id: int):
        df, update_date = BotStatistics._get_elo_data(bot_id, competition_id)
        if not df.empty:
            df.columns = ["Name", "ELO", "Date"]

            # if the bot was updated more recently than the first result datetime, then use the bot updated date
            update_date = update_date[0][0]
            if update_date.tzinfo:
                update_date = utc.normalize(update_date)  # convert from a tuple
            else:
                update_date = utc.localize(update_date)

            bot_updated_datetime = Bot.objects.get(id=bot_id).bot_zip_updated
            if bot_updated_datetime > update_date:
                update_date = bot_updated_datetime

            return BotStatistics._generate_elo_plot_images(df, update_date)
        else:
            return None

    @staticmethod
    def _get_winrate_data(bot_id, competition_id):
        # this does not distinct between competitions
        with connection.cursor() as cursor:
            query = f"""
                select duration_minutes,
                    count(CASE WHEN is_winner THEN 1 END) as wins,
                    count(CASE WHEN is_loser THEN 1 END) as losses,
                    count(CASE WHEN is_crasher THEN 1 END) as crashes,
                    count(CASE WHEN is_tied THEN 1 END) as ties
                from
                    (select
                        (cp.result = 'win') as is_winner,
                        (cp.result = 'loss' and cp.result_cause != 'crash') as is_loser,
                        (cp.result_cause = 'crash') as is_crasher,
                        (cp.result = 'tie') as is_tied,
                        floor(cr.game_steps/((22.4*60)*5))*5 as duration_minutes
                    from core_matchparticipation cp
                        inner join core_result cr on cp.match_id = cr.match_id
                        left join core_bot cb on cp.bot_id = cb.id
                        left join core_match cm on cp.match_id = cm.id
                        left join core_round crnd on cm.round_id = crnd.id
                        left join core_competition cc on crnd.competition_id = cc.id
                    where bot_id = {bot_id}
                        and competition_id = {competition_id}) matches
                    group by duration_minutes
                    order by duration_minutes
                """
            cursor.execute(query)
            stats_vs_duration = pd.DataFrame(cursor.fetchall())

        return stats_vs_duration

    @staticmethod
    def _generate_winrate_plot_images(df):
        plot1 = io.BytesIO()

        legend = []

        durations = df["Duration (Minutes)"].map(lambda x: str(x) + " - " + str(x + 5))
        wins = df["Wins"]
        losses = df["Losses"]
        crashes = df["Crashes"]
        ties = df["Ties"]
        totals = [w + l + c + t for w, l, c, t in zip(wins, losses, crashes, ties)]

        width = 0.65

        fig, ax1 = plt.subplots(1, 1, figsize=(12, 9), sharex="all", sharey="all")
        ax1.bar(durations, wins, width, color="#86C232", label="Wins")
        ax1.bar(durations, ties, width, color="#DFCE00", bottom=wins, label="Ties")
        ax1.bar(durations, losses, width, color="#D20044", bottom=wins + ties, label="Losses")
        ax1.bar(durations, crashes, width, color="#AAAAAA", bottom=wins + ties + losses, label="Crashes")
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.spines["left"].set_color("#86c232")
        ax1.spines["bottom"].set_color("#86c232")
        ax1.autoscale(enable=True, axis="x")
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()
        ax1.yaxis.get_major_locator().set_params(integer=True)
        ax1.tick_params(axis="x", colors="#86c232", labelsize=16)
        ax1.tick_params(axis="y", colors="#86c232", labelsize=16)
        ax1.legend(loc="upper right", fontsize="xx-large")

        effect = [path_effects.Stroke(linewidth=3, foreground="black"), path_effects.Normal()]

        for i, val in enumerate(zip(wins, losses, crashes, ties, totals)):
            c_totals = val[4]
            if c_totals == 0:
                continue
            c_wins = val[0]
            c_losses = val[1]
            c_crashes = val[2]
            c_ties = val[3]
            if c_wins > 0:
                plt.text(
                    i,
                    c_wins / 2,
                    str(round(c_wins / c_totals * 100)) + "%",
                    va="center",
                    ha="center",
                    color="#FFFFFF",
                    size=20,
                ).set_path_effects(effect)
            if c_ties > 0:
                plt.text(
                    i,
                    c_wins + c_ties / 2,
                    str(round(c_ties / c_totals * 100)) + "%",
                    va="center",
                    ha="center",
                    color="#FFFFFF",
                    size=20,
                ).set_path_effects(effect)
            if c_losses > 0:
                plt.text(
                    i,
                    c_wins + c_ties + c_losses / 2,
                    str(round(c_losses / c_totals * 100)) + "%",
                    va="center",
                    ha="center",
                    color="#FFFFFF",
                    size=20,
                ).set_path_effects(effect)
            if c_crashes > 0:
                plt.text(
                    i,
                    c_wins + c_ties + c_losses + c_crashes / 2,
                    str(round(c_crashes / c_totals * 100)) + "%",
                    va="center",
                    ha="center",
                    color="#FFFFFF",
                    size=20,
                ).set_path_effects(effect)

        plt.title("Result vs Match Duration", fontsize=20, color=("#86c232"))
        plt.tight_layout()  # Avoids savefig cutting off x-label
        plt.savefig(plot1, format="png", transparent=True)
        plt.xticks(durations)

        plt.close(fig)
        return plot1

    @staticmethod
    def _generate_winrate_graph(bot_id: int, competition_id: int):
        df = BotStatistics._get_winrate_data(bot_id, competition_id)
        if not df.empty:
            df.columns = ["Duration (Minutes)", "Wins", "Losses", "Crashes", "Ties"]
            return BotStatistics._generate_winrate_plot_images(df)
        else:
            return None
