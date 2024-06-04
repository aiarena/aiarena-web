import logging

from django.db import transaction

from aiarena.core.models import (
    Map,
    WebsiteUser, )
from aiarena.core.models.game_mode import GameMode
from aiarena.core.services.internal.match_requests import handle_request_match, handle_request_matches

logger = logging.getLogger(__name__)


class MatchRequests:
    @staticmethod
    def request_matches(requested_by_user: WebsiteUser, bot1, opponent, match_count, matchup_race, matchup_type, map_selection_type, map_pool, chosen_map):
        """
        Request a number of matches between two bots, with the given parameters.
        """
        with transaction.atomic():
            return handle_request_matches(requested_by_user, bot1, opponent, match_count, matchup_race, matchup_type, map_selection_type, map_pool, chosen_map)

    @staticmethod
    def request_match(user: WebsiteUser, bot, opponent, map: Map = None, game_mode: GameMode = None):
        """
        Request a single match between two bots, with the given parameters.
        """
        with transaction.atomic():
            return handle_request_match(bot, game_mode, map, opponent, user)
