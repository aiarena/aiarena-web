from django.db import connection
from django.http import HttpResponse


def health_check(*args, **kwargs):
    return HttpResponse("OK")


def health_check_with_db(*args, **kwargs):
    # test database connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")

    return HttpResponse("OK")
