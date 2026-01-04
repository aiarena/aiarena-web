from ._arena_clients import ArenaClients as _ArenaClientsClass
from ._bot_statistics import BotStatistics as _BotStatisticsClass
from ._bots import Bots as _BotsClass
from ._competitions import Competitions as _CompetitionsClass
from ._ladders import Ladders as _LaddersClass
from ._match_requests import MatchRequests as _MatchRequestsClass
from ._matches import Matches as _MatchesClass
from ._supporter_benefits import SupporterBenefits as _SupporterBenefitsClass
from ._users import Users as _UsersClass


arena_clients = _ArenaClientsClass()
bot_statistics = _BotStatisticsClass()
bots = _BotsClass()
competitions = _CompetitionsClass()
ladders = _LaddersClass()
match_requests = _MatchRequestsClass()
matches = _MatchesClass(bots, competitions)
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
