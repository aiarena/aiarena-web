import os

from aiarena.settings import SCRIPTS_ROOT
from django.db import connection


def run_usp_generate_stats_sql():
    pass
    # no longer present
    # file_path = os.path.join(SCRIPTS_ROOT, 'usp_generate_stats.sql')
    # sql_statement = open(file_path).read()
    # with connection.cursor() as c:
    #     # Drop the stored procedure if it already exists
    #     c.execute("DROP PROCEDURE IF EXISTS `generate_stats`;")
    #     # Then create it...
    #     c.execute(sql_statement)
