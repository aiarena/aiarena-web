from django.apps import AppConfig

from aiarena.core.events.event_manager import EventManager


class CoreConfig(AppConfig):
    name = 'aiarena.core'

    def ready(self):
        EVENT_MANAGER = EventManager()
