import io

import matplotlib.pyplot as plt
import pandas as pd
from django.db import connection

from aiarena.core.models import Bot, StatsBots


class StatsGenerator:

    @staticmethod
    def generate_stats():
        with connection.cursor() as c:
            c.callproc("generate_stats")

        StatsGenerator._generate_graphs()

    @staticmethod
    def _get_data(bot_id):
        with connection.cursor() as cursor:
            query = ("""
                select distinct
                cb.name, 
                avg(cp.resultant_elo) as elo, 
                date(cm.created) as date 
                from core_participation cp
                    left join core_match cm on cp.match_id = cm.id
                    left join core_bot cb on cp.bot_id = cb.id
                where resultant_elo is not null 
                    and bot_id = """ + str(bot_id) + """ 
                group by date(cm.created) 
                order by cm.created
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
    def _generate_graphs():
        for bot in Bot.get_active():
            df = StatsGenerator._get_data(bot.id)
            if not df.empty:
                df[1] = pd.to_numeric(df[1])
                df.columns = ['Name', 'ELO', 'Date']

                plot = StatsGenerator._generate_plot_image(df)

                statsbot = StatsBots.objects.get(bot=bot)
                statsbot.elo_graph.save('elo.png', plot)  # the filename here will do nothing - it's just required
