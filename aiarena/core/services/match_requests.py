import logging

from django.db import transaction

from aiarena.core.models import (
    Map,
    User,
    WebsiteUser,
)
from aiarena.core.models.game_mode import GameMode

from .internal.match_requests import get_user_match_request_count_left, handle_request_match, handle_request_matches


logger = logging.getLogger(__name__)


class MatchRequests:
    def request_matches(
        requested_by_user: WebsiteUser,
        bot1,
        opponent,
        match_count,
        matchup_race,
        matchup_type,
        map_selection_type,
        map_pool,
        chosen_map,
    ):
        """
        Request a number of matches between two bots, with the given parameters.
        """
        with transaction.atomic():
            return handle_request_matches(
                requested_by_user,
                bot1,
                opponent,
                match_count,
                matchup_race,
                matchup_type,
                map_selection_type,
                map_pool,
                chosen_map,
            )

    def request_match(self, user: WebsiteUser, bot, opponent, map: Map = None, game_mode: GameMode = None):
        """
        Request a single match between two bots, with the given parameters.
        """
        with transaction.atomic():
            return handle_request_match(bot, game_mode, map, opponent, user)

    def get_user_match_request_count_left(self, user: User):
        """
        Get the number of match requests a user can make.
        """
        return get_user_match_request_count_left(user)
