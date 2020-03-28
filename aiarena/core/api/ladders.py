import logging

from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.urls import reverse

from aiarena import settings
from aiarena.core.models import Bot, Season, SeasonParticipation

logger = logging.getLogger(__name__)


class Ladders:
    @staticmethod
    def get_season_ranked_participants(season: Season):
        return SeasonParticipation.objects.filter(season_id=season.id, bot__active=True).order_by('-elo')

