from .arena_clients import ArenaClients as _ArenaClientsClass
from .bot_statistics import BotStatistics as _BotStatisticsClass
from .bots import Bots as _BotsClass
from .competitions import Competitions as _CompetitionsClass
from .ladders import Ladders as _LaddersClass
from .match_requests import MatchRequests as _MatchRequestsClass
from .matches import Matches as _MatchesClass
from .supporter_benefits import SupporterBenefits as _SupporterBenefitsClass
from .users import Users as _UsersClass

arena_clients = _ArenaClientsClass()
bot_statistics = _BotStatisticsClass()
bots = _BotsClass()
competitions = _CompetitionsClass()
ladders = _LaddersClass()
match_requests = _MatchRequestsClass()
matches = _MatchesClass()
supporter_benefits = _SupporterBenefitsClass()
users = _UsersClass()

__all__ = [
    "arena_clients",
    "bot_statistics",
    "bots",
    "competitions",
    "ladders",
    "match_requests",
    "matches",
    "supporter_benefits",
    "users",
]
