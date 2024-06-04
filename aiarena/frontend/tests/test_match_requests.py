from django.test import TestCase

from aiarena.core.models import Bot, Map, MapPool
from aiarena.core.tests.test_mixins import FullDataSetMixin

class RequestMatchTestCase(FullDataSetMixin, TestCase):
    def test_request_match_regular_user(self):
        # log in as a regular user
        self.test_client.login(self.regularUser1)
        bot1 = Bot.objects.all().first()
        bot2 = Bot.objects.all().last()
        map = Map.objects.all().first()

        # Request specific map
        self.test_client.request_match("specific_matchup", bot1, bot2, "any", "specific_map", map, None, 3)

        # Request map pool
        self.test_client.request_match(
            "specific_matchup", bot1, bot2, "any", "map_pool", None, MapPool.objects.first(), 3
        )
