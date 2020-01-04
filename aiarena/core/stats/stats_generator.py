import io

import matplotlib.pyplot as plt
import pandas as pd
from django.db import connection

from aiarena.core.models import Bot, Season, MatchParticipation, SeasonParticipation


class StatsGenerator:

    @staticmethod
    def update_stats(bot: Bot):
        current_season: Season = Season.get_current_season()
        sp: SeasonParticipation = bot.current_season_participation()
        sp.match_count = MatchParticipation.objects.filter(bot=bot,
                                                           result__isnull=False,
                                                           match__round__season=current_season).count()
        if sp.match_count != 0:
            sp.win_perc \
                = MatchParticipation.objects.filter(bot=bot, match__result__is='win',
                                                    match__round__season=current_season
                                                    ).count() / sp.match_count
            sp.crash_perc \
                = MatchParticipation.objects.filter(bot=bot, result='loss', result_cause__in=['crash',
                                                                                              'timeout',
                                                                                              'initialization_failure'],
                                                    match__round__season=current_season
                                                    ).count() / sp.match_count
            graph = StatsGenerator._generate_elo_graph(bot.id)
            if graph is not None:
                sp.elo_graph.save('elo.png', graph)
        sp.save()

    @staticmethod
    def _get_data(bot_id):
        with connection.cursor() as cursor:
            query = (f"""
                select distinct
                avg(cp.resultant_elo) as elo, 
                date(cr.created) as date 
                from core_matchparticipation cp
                    inner join core_result cr on cp.match_id = cr.match_id
                where resultant_elo is not null 
                    and bot_id = {bot_id} 
                group by date(cr.created) 
                order by cr.created
                """)
            cursor.execute(query)
            elo_over_time = pd.DataFrame(cursor.fetchall())
        return elo_over_time

    @staticmethod
    def _generate_plot_image(df):
        plot = io.BytesIO()
        ax = plt.gca()
        graph = df.plot(kind='line', x='Date', y='ELO', ax=ax, figsize=(12, 9), color=('#86c232'))
        graph.spines["top"].set_visible(False)
        graph.spines["right"].set_visible(False)
        graph.spines["left"].set_color('#86c232')
        graph.spines["bottom"].set_color('#86c232')
        graph.autoscale(enable=True, axis='x')
        graph.get_xaxis().tick_bottom()
        graph.get_yaxis().tick_left()

        plt.title('ELO over time', fontsize=20, color=('#86c232'))
        plt.xticks(rotation=60)
        ax.xaxis.label.set_color('#86c232')
        ax.tick_params(axis='x', colors='#86c232')
        ax.tick_params(axis='y', colors='#86c232')
        plt.tight_layout()  # Avoids savefig cutting off x-label
        plt.savefig(plot, format="png", transparent=True)
        plt.cla()  # Clears axis in preparation for new graph
        return plot

    @staticmethod
    def _generate_elo_graph(bot_id: int):
        df = StatsGenerator._get_data(bot_id)
        if not df.empty:
            df[1] = pd.to_numeric(df[1])
            df.columns = ['ELO', 'Date']

            return StatsGenerator._generate_plot_image(df)
        else:
            return None
