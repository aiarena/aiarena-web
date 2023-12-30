import io
from datetime import datetime

from django.db import connection

import matplotlib
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from pytz import utc

from aiarena.core.models import Bot, CompetitionParticipation


# Use the AGG backend - https://matplotlib.org/stable/users/explain/figure/backends.html#static-backends
matplotlib.use("agg")


class EloGraphsGenerator:
    def __init__(self, sp: CompetitionParticipation):
        self.sp = sp

    def generate(self) -> (io.BytesIO, io.BytesIO, io.BytesIO):
        graph1, graph2 = self._generate_elo_graph(self.sp.bot, self.sp.competition_id)
        graph3 = self._generate_winrate_graph(self.sp.bot.id, self.sp.competition_id)
        return graph1, graph2, graph3

    def _generate_elo_graph(self, bot: Bot, competition_id: int):
        df = self._get_elo_data_frame(bot, competition_id)

        if df.empty:
            return None, None  # no elo data

        df.columns = ["Name", "ELO", "Date"]

        update_date = self._get_graph_update_line_datetime(bot, competition_id)

        return self._generate_elo_plot_images(df, update_date)

    def _get_graph_update_line_datetime(self, bot, competition_id):
        update_date = self.get_earliest_result_datetime(bot.id, competition_id)[0][0]
        update_date = utc.normalize(update_date) if update_date.tzinfo else utc.localize(update_date)
        # use the most recent date for the graph update line
        return max(update_date, bot.bot_zip_updated)

    def _generate_winrate_graph(self, bot_id: int, competition_id: int):
        df = self._get_winrate_data(bot_id, competition_id)
        if not df.empty:
            df.columns = ["Duration (Minutes)", "Wins", "Losses", "Crashes", "Ties"]
            return self._generate_winrate_plot_images(df)
        else:
            return None

    def _get_winrate_data(self, bot_id, competition_id):
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

    def _generate_winrate_plot_images(self, df):
        plot1 = io.BytesIO()

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

    def _get_elo_data_frame(self, bot, competition_id):
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
                    and bot_id = {bot.id} 
                    and competition_id = {competition_id}
                order by cr.created
                """
            cursor.execute(query)
            elo_over_time = pd.DataFrame(cursor.fetchall())

        return elo_over_time

    def get_earliest_result_datetime(self, bot_id, competition_id):
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

    def _generate_elo_plot_images(self, df, update_date: datetime):
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
