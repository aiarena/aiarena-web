import os

from django.conf import settings

from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiarena.settings")

app = Celery("aiarena")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
    app.conf.CELERY_TASK_ALWAYS_EAGER = True
