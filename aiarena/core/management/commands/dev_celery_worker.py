import shlex

from django.core.management.base import BaseCommand
from django.utils import autoreload

from aiarena.celery import app


class Command(BaseCommand):
    @staticmethod
    def restart_celery():
        app.worker_main(shlex.split("worker -l INFO -Q default -P solo --concurrency 1"))

    def handle(self, *args, **options):
        autoreload.run_with_reloader(self.restart_celery)
