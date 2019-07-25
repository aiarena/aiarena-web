import os

from aiarena.settings import SCRIPTS_ROOT
from django.db import connection


def run_usp_generate_stats_sql():
    file_path = os.path.join(SCRIPTS_ROOT, 'usp_generate_stats.sql')
    sql_statement = open(file_path).read()
    with connection.cursor() as c:
        c.executemany(sql_statement, [])