# ruff: noqa: F401
from .bot_statistics import BotStatistics
from .bots import Bots
from .competitions import Competitions
from .ladders import Ladders
from .match_requests import MatchRequests
from .matches import Matches
from .supporter_benefits import SupporterBenefits
from .users import Users

from .arena_clients import ArenaClients as _ArenaClientsClass

arena_clients = _ArenaClientsClass()

__all__ = [
    "BotStatistics",
    "Bots",
    "Competitions",
    "Ladders",
    "MatchRequests",
    "Matches",
    "SupporterBenefits",
    "Users",
    "arena_clients",
]
