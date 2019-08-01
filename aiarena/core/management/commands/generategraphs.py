from django.db import connection
from django.core.management.base import BaseCommand
import pandas as pd
import matplotlib.pyplot as plt

# ToDo: Use django configuration
# config = {
#   'user': 'root',
#   'password': '',
#   'host': '127.0.0.1',
#   'database': '',
#   'raise_on_warnings': True
# }


# cnx = connector.connect(**config)
class Command(BaseCommand):
    help = 'Generates bot statistic graphs.'
    def get_active_bot_ids(self):
        with connection.cursor() as cursor:
            #cursor = cnx.cursor()
            query =('''
            SELECT 
            ID 
            FROM AIARENA_BETA.CORE_BOT
            WHERE ACTIVE = 1''')
            cursor.execute(query)
            bots = [x[0] for x in cursor.fetchall()]
        return bots

    def get_data(self, bot_id):
        with connection.cursor() as cursor:
        #cursor = cnx.cursor()
            query = ("""
                SELECT DISTINCT 
                CB.NAME, 
                AVG(CP.RESULTANT_ELO) AS ELO, 
                DATE(CM.CREATED) AS DATE 
                FROM AIARENA_BETA.CORE_PARTICIPANT CP
                    LEFT JOIN AIARENA_BETA.CORE_MATCH CM ON CP.MATCH_ID = CM.ID
                    LEFT JOIN AIARENA_BETA.CORE_BOT CB ON CP.BOT_ID = CB.ID
                WHERE RESULTANT_ELO IS NOT NULL 
                    AND BOT_ID = """+str(bot_id)+""" 
                GROUP BY DATE(CM.CREATED) 
                ORDER BY CM.CREATED
                """)
            cursor.execute(query)
            elo_over_time = pd.DataFrame(cursor.fetchall())
        return elo_over_time

    def generate_and_save_plot(self, df, path):
        ax = plt.gca()
        graph=df.plot(kind='line',x='Date',y='ELO',ax=ax,figsize=(12, 9),color=('#86c232'))
        graph.spines["top"].set_visible(False)   
        graph.spines["right"].set_visible(False)
        graph.spines["left"].set_color('#86c232')
        graph.spines["bottom"].set_color('#86c232')
        graph.autoscale(enable=True, axis='x')
        graph.get_xaxis().tick_bottom()    
        graph.get_yaxis().tick_left()

        plt.title('ELO over time', fontsize=20,color=('#86c232'))
        plt.xticks(rotation=60)
        ax.xaxis.label.set_color('#86c232')
        ax.tick_params(axis='x', colors='#86c232')
        ax.tick_params(axis='y', colors='#86c232')
        plt.tight_layout() # Avoids savefig cutting off x-label
        plt.savefig(path, transparent=True)
        plt.cla() # Clears axis in preparation for new graph
        
    def handle(self, *args, **options):
        self.stdout.write('Generating graphs...')
        for bot_id in self.get_active_bot_ids():
            path = '../static/graph/' + str(bot_id) + "/elo.png"
            
            df=self.get_data(bot_id)

            df[1] = pd.to_numeric(df[1])
            df.columns = ['Name','ELO','Date']

            self.generate_and_save_plot(df, path)
        self.stdout.write('Done')