from enum import Enum

from aiarena.core.models import Result, Bot
from aiarena.core.utils import post_result_to_discord_bot


class EventType(Enum):
    MATCH_RESULT_RECEIVED = 1
    BOT_ACTIVATION_STATUS_CHANGED = 2


class Event:
    TYPE = None


class MatchResultReceivedEvent(Event):
    TYPE = EventType.MATCH_RESULT_RECEIVED

    def __init__(self, result: Result):
        self.result = result


class BotActivationStatusChangedEvent(Event):
    TYPE = EventType.BOT_ACTIVATION_STATUS_CHANGED

    def __init__(self, bot: Bot):
        self.bot = bot
