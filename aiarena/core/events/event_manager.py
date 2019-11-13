from aiarena.core.events.events import BotActivationStatusChangedEvent, MatchResultReceivedEvent, Event, EventType
from aiarena.core.utils import post_result_to_discord_bot


class EventManager:
    def __init__(self):
        self._EVENT_HANDLER_MAP = {
            EventType.MATCH_RESULT_RECEIVED: self._handle_match_result_received,
            EventType.BOT_ACTIVATION_STATUS_CHANGED: self._handle_bot_activation_status_changed
        }

    def broadcast_event(self, event: Event):
        self._EVENT_HANDLER_MAP[event.TYPE](event)

    def _handle_match_result_received(self, event: MatchResultReceivedEvent):
        post_result_to_discord_bot(event.result)

    # todo: change this to a generic bot updated event
    def _handle_bot_activation_status_changed(self, event: BotActivationStatusChangedEvent):
        pass


EVENT_MANAGER = EventManager()
