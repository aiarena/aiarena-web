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

class SupporterBenefits:
    @staticmethod
    def get_bot_limit(user: User):
        limit = BOTS_LIMIT_MAP[user.patreon_level]
        if limit is None:
            return None  # no limit
        else:
            return limit + user.extra_active_competition_participations