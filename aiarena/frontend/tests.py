from django.urls import reverse
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from aiarena.core.models import Match, Round, Bot, User, Map, Result, Season
from aiarena.core.tests.tests import FullDataSetMixin
from .admin import MapAdmin, MatchAdmin, SeasonAdmin
from aiarena.settings import TestCase, TransactionTestCase


class AdminMethodsTestCase(FullDataSetMixin, TestCase):

   # admin uses this functionality
    def test_map_admin(self):
        self.factory = RequestFactory()
        test_maps = Map.objects.all()
        admin = MapAdmin(model=Map, admin_site='/admin')
        request = self.factory.get('/admin')
        request.user = User.objects.first()
        admin.deactivate(request, test_maps)
        for tmap in test_maps:
            self.assertFalse(tmap.active, msg=f"failed to deactivate Map<{tmap}> Using the admin interface ")
        admin.activate(request, test_maps)
        for tmap in test_maps:
            self.assertTrue(tmap.active, msg=f"failed to activate Map<{tmap}> Using the admin interface ")

    def test_match_admin(self):
        self.factory = RequestFactory()
        test_matches= Match.objects.all()
        admin = MatchAdmin(model=Map, admin_site='/admin')
        request = self.factory.get('/admin')
        request.user = User.objects.first()
        no_result_matches = []
        for match in test_matches:
            results = Result.objects.filter(match=match)
            if len(results): # this match has a result pre made in the test db
                continue
            no_result_matches.append(match)
        admin.cancel_matches(request, no_result_matches)
        for match in no_result_matches:
            result = Result.objects.get(match=match)
            self.assertTrue(result.type == "MatchCancelled", msg=f"failed to Cancel Match<{match}>, Result<{result}> Using the admin interface ")

    """ need to make this one work """
    def test_season_admin(self):
        self.factory = RequestFactory()
        admin = SeasonAdmin(model=Season, admin_site='/admin')
        season = Season.objects.first()
        data = {'action': '_pause-season',
                '_selected_action': [season, ]}
        class dumb_hack:
            def __init__(self, name):
                self.name = name



        def mock_request_admin(factory, data, admin):
            request = factory.post(reverse("admin:index"), data=data)
            request.user = User.objects.first()
            """Annotate a request object with a session"""
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            """Annotate a request object with a messages"""
            middleware = MessageMiddleware()
            middleware.process_request(request)
            request.session.save()
            admin.admin_site = dumb_hack(name=admin.admin_site)
            return request, admin

        request, admin = mock_request_admin(self.factory,data,admin)
        self.assertEqual(season.status, 'open', msg=f"first season in the test database is not open!")
        admin.response_change(request, season)
        self.assertEqual(season.status, 'paused', msg=f"failed responsechange<pause> on Season<{season}> Using the admin interface ")

        data['action'] = "_open-season"
        request, admin = mock_request_admin(self.factory, data, admin)
        admin.response_change(request, season)
        self.assertEqual(season.status, 'open', msg=f"failed responsechange<open> on Season<{season}> Using the admin interface ")

        data['action'] = "_close-season"
        request, admin = mock_request_admin(self.factory, data, admin)
        admin.response_change(request, season)
        self.assertEqual(season.status, 'closing', msg=f"failed responsechange<closing> on Season<{season}> Using the admin interface ")



class PageRenderTestCase(FullDataSetMixin, TransactionTestCase):
    """
    Tests to ensure website pages don't break.
    """

    def test_render_pages(self):
        # index
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # login
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

        # register
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

        # bots
        response = self.client.get('/bots/')
        self.assertEqual(response.status_code, 200)

        # profile before login - should redirect
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

        # bot
        active_bot = Bot.objects.filter(active=True)[0]
        response = self.client.get('/bots/{0}/'.format(active_bot.id))
        self.assertEqual(response.status_code, 200)

        # bot edit
        self.client.login(username='regular_user1', password='x')
        # test bot edit pages we can access
        bots = Bot.objects.filter(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit/'.format(bot.pk))
            self.assertEqual(response.status_code, 200)

        # test bot edit pages we can't access
        bots = Bot.objects.exclude(user=self.regularUser1)
        for bot in bots:
            response = self.client.get('/bots/{0}/edit/'.format(bot.pk))
            self.assertEqual(response.status_code, 404)

        # authors
        response = self.client.get('/authors/')
        self.assertEqual(response.status_code, 200)

        # author
        response = self.client.get('/authors/{0}/'.format(self.regularUser1.id))
        self.assertEqual(response.status_code, 200)

        # match
        response = self.client.get('/matches/{0}/'.format(Match.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)

        # ranking
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 302)

        # results
        response = self.client.get('/results/')
        self.assertEqual(response.status_code, 200)

        # password_reset
        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

        # stream
        response = self.client.get('/stream/')
        self.assertEqual(response.status_code, 200)

        # match-queue
        response = self.client.get('/match-queue/')
        self.assertEqual(response.status_code, 200)

        # round
        response = self.client.get('/rounds/{0}/'.format(Round.objects.all()[0].id))
        self.assertEqual(response.status_code, 200)

        # arenaclients
        response = self.client.get('/arenaclients/')
        self.assertEqual(response.status_code, 200)

        # arenaclients
        for arenaclient in User.objects.filter(type='ARENA_CLIENT'):
            response = self.client.get('/arenaclients/{0}/'.format(arenaclient.id))
            self.assertEqual(response.status_code, 200)

        # profile
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

        # token
        response = self.client.get('/profile/token/')
        self.assertEqual(response.status_code, 200)

        # recreate - will redirect
        response = self.client.post('/profile/token/')
        self.assertEqual(response.status_code, 302)

        # requestmatch
        response = self.client.get('/requestmatch/')
        self.assertEqual(response.status_code, 200)
