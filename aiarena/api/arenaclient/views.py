import logging
from wsgiref.util import FileWrapper

from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, serializers, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.fields import FileField
from rest_framework.response import Response
from rest_framework.reverse import reverse

from aiarena.api.arenaclient.exceptions import NotEnoughAvailableBots, NotEnoughActiveBots, NoMaps
from aiarena.core.exceptions import BotNotInMatchException
from aiarena.core.models import Bot, Map, Match, Participant, Result
from aiarena.settings import ELO_START_VALUE, ENABLE_ELO_SANITY_CHECK, ELO

logger = logging.getLogger(__name__)


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class BotSerializer(serializers.ModelSerializer):
    # Dynamically regenerate bot_zip and bot_data urls to point to the API endpoints
    # Otherwise they will point to the front-end download views, which the API client won't
    # be authenticated for.
    bot_zip = serializers.SerializerMethodField()
    bot_data = serializers.SerializerMethodField()

    def get_bot_zip(self, obj):
        p = Participant.objects.get(bot=obj, match=obj.current_match)
        return reverse('match-download-zip', kwargs={'pk': obj.current_match.pk, 'p_num': p.participant_number},
                       request=self.context['request'])

    def get_bot_data(self, obj):
        p = Participant.objects.get(bot=obj, match=obj.current_match)
        if p.bot.bot_data:
            return reverse('match-download-data', kwargs={'pk': obj.current_match.pk, 'p_num': p.participant_number},
                           request=self.context['request'])
        else:
            return None

    class Meta:
        model = Bot
        fields = ('id', 'name', 'bot_zip', 'bot_zip_md5hash', 'bot_data', 'bot_data_md5hash', 'plays_race', 'type')


class MatchSerializer(serializers.ModelSerializer):
    bot1 = BotSerializer(read_only=True)
    bot2 = BotSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Match
        fields = ('id', 'bot1', 'bot2', 'map')


class MatchViewSet(viewsets.GenericViewSet):
    """
    MatchViewSet implements a POST method with no field requirements, which will create a match and return the JSON.
    No reading of models is implemented.
    """
    serializer_class = MatchSerializer

    def create(self, request, *args, **kwargs):
        if Map.objects.count() == 0:
            raise NoMaps()
        if Bot.objects.filter(active=True).count() <= 1:  # need at least 2 active bots for a match
            raise NotEnoughActiveBots()

        Bot.timeout_overtime_bot_games()
        if Bot.objects.filter(active=True, in_match=False).count() <= 1:  # need at least 2 bots that aren't in game
            raise NotEnoughAvailableBots()

        match = Match.objects.create(map=Map.random())

        # Add participating bots
        bot1 = Bot.get_random_available()
        bot2 = bot1.get_random_available_excluding_self()

        # create match participants
        Participant.objects.create(match=match, participant_number=1, bot=bot1)
        Participant.objects.create(match=match, participant_number=2, bot=bot2)

        # mark bots as in match
        bot1.enter_match(match)
        bot2.enter_match(match)

        # return bot data along with the match
        match.bot1 = bot1
        match.bot2 = bot2

        serializer = self.get_serializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s zip file', url_path='(?P<p_num>\d+)/zip')
    def download_zip(self, request, *args, **kwargs):
        p = Participant.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_zip), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}.zip"'.format(p.bot.name)
        return response

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s data file', url_path='(?P<p_num>\d+)/data')
    def download_data(self, request, *args, **kwargs):
        p = Participant.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_data), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}_data.zip"'.format(p.bot.name)
        return response


class ResultSerializer(serializers.ModelSerializer):
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)

    def validate(self, attrs):
        # remove the bot datas so they don't cause validation failure
        modified_attrs = attrs.copy()
        if 'bot1_data' in attrs:
            modified_attrs.pop('bot1_data')
        if 'bot2_data' in attrs:
            modified_attrs.pop('bot2_data')
        instance = ResultSerializer.Meta.model(**modified_attrs)

        instance.clean()  # enforce model validation because result has some custom checks
        return attrs

    class Meta:
        model = Result
        fields = 'type', 'replay_file', 'duration', 'match', 'bot1_data', 'bot2_data'


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """
    serializer_class = ResultSerializer

    # todo: avoid results being logged against matches not owned by the submitter
    def perform_create(self, serializer):
        # pop bot datas so they don't interfere with saving the result
        process_bot1_data = False
        process_bot2_data = False
        if 'bot1_data' in serializer.validated_data:
            bot1_data = serializer.validated_data.pop('bot1_data')
            process_bot1_data = True
        if 'bot2_data' in serializer.validated_data:
            bot2_data = serializer.validated_data.pop('bot2_data')
            process_bot2_data = True

        result = serializer.save()
        p1_initial_elo, p2_initial_elo = self.get_initial_elos(result)
        self.adjust_elo(result)
        p1, p2 = result.get_participants()
        p1.update_resultant_elo()
        p2.update_resultant_elo()
        # calculate the change in ELO
        p1.elo_change = p1.resultant_elo - p1_initial_elo
        p1.save()
        p2.elo_change = p2.resultant_elo - p2_initial_elo
        p2.save()

        if ENABLE_ELO_SANITY_CHECK:  # todo remove this condition and log instead of an exception.
            # test here to check ELO total and ensure no corruption
            sumElo = Bot.objects.aggregate(Sum('elo'))
            if sumElo['elo__sum'] != ELO_START_VALUE * Bot.objects.all().count():
                logger.critical("ELO did not sum to expected value upon submission of result {0}".format(result.id))

        bot1 = serializer.validated_data['match'].participant_set.get(participant_number=1).bot
        bot2 = serializer.validated_data['match'].participant_set.get(participant_number=2).bot

        # save bot datas
        if process_bot1_data:
            bot1.bot_data = bot1_data
            bot1.save()

        if process_bot2_data:
            bot2.bot_data = bot2_data
            bot2.save()

        try:
            bot1.leave_match()
            bot2.leave_match()
        except BotNotInMatchException:
            raise APIException('Unable to log result - one of the bots is not listed as in a match.')

    def adjust_elo(self, result):
        if result.has_winner():
            winner, loser = result.get_winner_loser_bots()
            self.apply_elo_delta(ELO.calculate_elo_delta(winner.elo, loser.elo, 1.0), winner, loser)
        elif result.type == 'Tie':
            first, second = result.get_participant_bots()
            self.apply_elo_delta(ELO.calculate_elo_delta(first.elo, second.elo, 0.5), first, second)

    def apply_elo_delta(self, delta, bot1, bot2):
        delta = int(round(delta))
        bot1.elo += delta
        bot1.save()
        bot2.elo -= delta
        bot2.save()

    def get_initial_elos(self, result):
        first, second = result.get_participant_bots()
        return first.elo, second.elo
