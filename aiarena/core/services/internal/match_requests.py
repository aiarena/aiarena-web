from django.utils import timezone

from constance import config

from aiarena.core.models import Map, Match, Result

from ...exceptions import MatchRequestException
from .. import bots
from ..supporter_benefits import SupporterBenefits
from .maps import Maps
from .matches import create


def _get_map(map_selection_type, map_pool, chosen_map):
    if map_selection_type == "map_pool":
        return Maps.random_from_map_pool(map_pool)
    else:
        return chosen_map


def get_user_match_request_count_left(user):
    return (
        SupporterBenefits.get_requested_matches_limit(user)
        - Match.objects.only("id")
        .filter(requested_by=user, created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD)
        .count()
        + Result.objects.only("id")
        .filter(
            submitted_by=user,
            type="MatchCancelled",
            created__gte=timezone.now() - config.REQUESTED_MATCHES_LIMIT_PERIOD,
        )
        .count()
    )


def handle_request_matches(
    requested_by_user, bot1, opponent, match_count, matchup_race, matchup_type, map_selection_type, map_pool, chosen_map
):
    if not config.ALLOW_REQUESTED_MATCHES:
        raise MatchRequestException("Sorry. Requested matches are currently disabled.")
    if bot1 == opponent:
        raise MatchRequestException("Sorry - you cannot request matches between the same bot.")
    if get_user_match_request_count_left(requested_by_user) < match_count:
        raise MatchRequestException("That number of matches exceeds your match request limit.")

    match_list = []
    if matchup_type == "random_ladder_bot":
        bot1 = bot1

        for _ in range(0, match_count):
            opponent = (
                bots.get_random_active_bot_excluding(bot1.id)
                if matchup_race == "any"
                else bots.get_active_excluding_bot(bot1).filter(plays_race__label=matchup_race).order_by("?").first()
            )

            if opponent is None:
                raise MatchRequestException("No opponents of that type could be found.")

            match_list.append(
                handle_request_match(
                    bot=bot1,
                    user=requested_by_user,
                    opponent=opponent,
                    map=_get_map(map_selection_type, map_pool, chosen_map),
                    game_mode=None,
                )
            )
    else:  # specific_matchup
        if opponent is None:
            raise MatchRequestException("Opponent is required for a specific matchup.")

        for _ in range(0, match_count):
            match_list.append(
                handle_request_match(
                    bot=bot1,
                    user=requested_by_user,
                    opponent=opponent,
                    map=_get_map(map_selection_type, map_pool, chosen_map),
                    game_mode=None,
                )
            )
    return match_list


def handle_request_match(bot, game_mode, map, opponent, user):
    # if map is none, a game mode must be supplied and a random map gets chosen
    if map is None:
        if game_mode:
            map = Maps.random_of_game_mode(game_mode)
        else:
            map = Map.objects.first()  # maybe improve this logic,  perhaps a random map and not just the first one
    return create(
        None,
        map,
        bot,
        opponent,
        user,
        bot1_update_data=False,
        bot2_update_data=False,
        require_trusted_arenaclient=False,
    )
