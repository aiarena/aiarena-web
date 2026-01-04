from ._bots import Bots
from ._supporters import Supporters
from .service_implementations import (
    ArenaClients as _ArenaClientsClass,
)
from .service_implementations import (
    Bots as _BotsClass,
)
from .service_implementations import (
    BotStatistics as _BotStatisticsClass,
)
from .service_implementations import (
    Competitions as _CompetitionsClass,
)
from .service_implementations import (
    Ladders as _LaddersClass,
)
from .service_implementations import (
    Matches as _MatchesClass,
)
from .service_implementations import (
    MatchRequests as _MatchRequestsClass,
)
from .service_implementations import (
    Supporters as _SupportersImplClass,
)
from .service_implementations import (
    Users as _UsersClass,
)


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
