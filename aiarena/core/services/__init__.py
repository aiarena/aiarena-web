from ._bots import Bots
from ._supporters import Supporters
from .service_implementations import (ArenaClients as _ArenaClientsClass,
                                      BotStatistics as _BotStatisticsClass,
                                      Bots as _BotsClass,
                                      Competitions as _CompetitionsClass,
                                      Ladders as _LaddersClass,
                                      MatchRequests as _MatchRequestsClass,
                                      Matches as _MatchesClass,
                                      Supporters as _SupportersImplClass,
                                      Users as _UsersClass)

supporters: Supporters = _SupportersImplClass()
arena_clients = _ArenaClientsClass()
bot_statistics = _BotStatisticsClass()
bots: Bots = _BotsClass()
competitions = _CompetitionsClass()
ladders = _LaddersClass()
match_requests = _MatchRequestsClass(supporters, bots)
matches = _MatchesClass(bots, competitions)
users = _UsersClass(supporters)

__all__ = [
    # Interfaces
    "Bots",
    "Supporters",
    # Implementations
    "arena_clients",
    "bot_statistics",
    "bots",
    "competitions",
    "ladders",
    "match_requests",
    "matches",
    "supporters",
    "users",
]
