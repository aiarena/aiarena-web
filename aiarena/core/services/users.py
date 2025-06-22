from aiarena.core.models import User
from aiarena.core.services import SupporterBenefits


class Users:
    @staticmethod
    def get_total_active_competition_participations(user: User):
        active_count = 0
        for bot in user.bots.all():
            active_count += bot.competition_participations.filter(active=True).count()
        return active_count

    @staticmethod
    def get_remaining_competition_participations(user: User):
        available_count = SupporterBenefits.get_active_bots_limit(
            user
        ) - Users.get_total_active_competition_participations(user)
        return available_count

    @staticmethod
    def ban_user(user: User) -> int:
        """
        Deactivate the user and disable all their bots' competition participations.
        Returns the number of participations disabled.
        """
        from aiarena.core.models import Bot
        from aiarena.core.services import Competitions

        user.is_active = False
        user.save()
        total_banned = 0
        bots = Bot.objects.filter(user=user)
        for bot in bots:
            total_banned += Competitions.disable_bot_for_all_competitions(bot)
        return total_banned
