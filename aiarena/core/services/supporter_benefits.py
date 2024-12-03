from django.conf import settings

from aiarena.core.models import User


BOTS_LIMIT_MAP = {
    "none": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER,
    "bronze": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER,
    "silver": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_SILVER_TIER,
    "gold": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_GOLD_TIER,
    "platinum": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_PLATINUM_TIER,
    "diamond": settings.MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DIAMOND_TIER,
}

REQUESTED_MATCHES_LIMIT_MAP = {
    "none": settings.MATCH_REQUEST_LIMIT_FREE_TIER,
    "bronze": settings.MATCH_REQUEST_LIMIT_BRONZE_TIER,
    "silver": settings.MATCH_REQUEST_LIMIT_SILVER_TIER,
    "gold": settings.MATCH_REQUEST_LIMIT_GOLD_TIER,
    "platinum": settings.MATCH_REQUEST_LIMIT_PLATINUM_TIER,
    "diamond": settings.MATCH_REQUEST_LIMIT_DIAMOND_TIER,
}


class SupporterBenefits:
    @staticmethod
    def get_bot_limit(user: User):
        limit = BOTS_LIMIT_MAP[user.patreon_level]
        if limit is None:
            return None  # no limit
        else:
            return limit + user.extra_active_competition_participations

    @staticmethod
    def get_requested_matches_limit(user: User):
        return REQUESTED_MATCHES_LIMIT_MAP[user.patreon_level] + user.extra_periodic_match_requests
