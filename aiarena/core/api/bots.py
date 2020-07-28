import logging

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.urls import reverse

from aiarena import settings
from aiarena.core.models import Bot

logger = logging.getLogger(__name__)


class Bots:
    @staticmethod
    def disable_and_send_crash_alert(bot: Bot):
        bot.active = False
        bot.save()
        try:
            send_mail(  # todo: template this
                'AI Arena - ' + bot.name + ' deactivated due to crashing',
                'Dear ' + bot.user.username + ',\n'
                                               '\n'
                                               'We are emailing you to let you know that your bot '
                                               '"' + bot.name + '" has reached our consecutive crash limit and hence been deactivated.\n'
                                                                 'Please log into ai-arena.net at your convenience to address the issue.\n'
                                                                 'Bot logs are available for download when logged in on the bot''s page here: '
                + settings.SITE_PROTOCOL + '://' + Site.objects.get_current().domain
                + reverse('bot', kwargs={'pk': bot.id}) + '\n'
                                                           '\n'
                                                           'Kind regards,\n'
                                                           'AI Arena Staff',
                settings.DEFAULT_FROM_EMAIL,
                [bot.user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_active() -> QuerySet:
        return Bot.objects.filter(active=True)

    @staticmethod
    def get_available(bots) -> list:
        return [bot for bot in bots if not bot.bot_data_is_currently_frozen()]

    @staticmethod
    def available_is_more_than(bots, amount: int) -> bool:
        available = 0
        for bot in bots:
            if not bot.bot_data_is_currently_frozen():
                available += 1
            if available >= amount:
                return True
        return False

