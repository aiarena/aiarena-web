import logging

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.urls import reverse

from constance import config

from aiarena import settings
from aiarena.core.models import Bot, Match


logger = logging.getLogger(__name__)


class Bots:
    def send_crash_alert(self, bot: Bot):
        # Can uncomment this if the emails show it isn't wrongly flagging bots
        # bot.competition_participations.update(active=False)
        try:
            send_mail(  # todo: template this
                "AI Arena - " + bot.name + " deactivated due to crashing",
                "Dear " + bot.user.username + ",\n"
                "\n"
                "We are emailing you to let you know that your bot "
                '"' + bot.name + '" has reached our consecutive crash limit and hence been deactivated.\n'
                "Please log into aiarena.net at your convenience to address the issue.\n"
                "Bot logs are available for download when logged in on the bot"
                "s page here: "
                + settings.SITE_PROTOCOL
                + "://"
                + Site.objects.get_current().domain
                + reverse("bot", kwargs={"pk": bot.id})
                + "\n"
                "\n"
                "Kind regards,\n"
                "AI Arena Staff",
                settings.DEFAULT_FROM_EMAIL,
                # change to bot.user.email (or add to list) when automatic disabling is turned on
                [config.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(e)

    def get_active(self) -> QuerySet:
        return Bot.objects.filter(competition_participations__active=True)

    def get_active_excluding_bot(self, bot: Bot) -> QuerySet:
        if self.get_active().count() <= 1:
            raise RuntimeError(f"Bot {bot.id} is the only bot.")
        return self.get_active().exclude(id=bot.id)

    def get_available(self, bots) -> list:
        return [bot for bot in bots if not self.bot_data_is_frozen(bot)]

    def available_is_more_than(self, bots, amount: int) -> bool:
        available = 0
        for bot in bots:
            if not self.bot_data_is_frozen(bot):
                available += 1
            if available >= amount:
                return True
        return False

    def get_random_active(self):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Bot.objects.filter(competition_participations__active=True).order_by("?").first()

    def get_random_active_bot_excluding(self, id):
        if self.get_active().count() <= 1:
            raise RuntimeError("I am the only bot.")
        bot = self.get_active().exclude(id=id).order_by("?").first()
        return bot

    def bot_data_is_frozen(self, bot) -> bool:
        # Check if there's any match where the bot's data is being used and updated
        data_frozen = Match.objects.filter(
            matchparticipation__bot=bot,
            matchparticipation__use_bot_data=True,
            matchparticipation__update_bot_data=True,
            started__isnull=False,
            result__isnull=True,
        ).exists()

        return bot.bot_data and data_frozen
