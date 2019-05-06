import logging

from django.db.models import Sum
from rest_framework import viewsets, serializers, mixins
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from aiarena.api.arenaclient.exceptions import EloSanityCheckException
from aiarena.core.models import Bot, Map, Match, Participant, Result
from aiarena.settings import ELO_START_VALUE, ENABLE_ELO_SANITY_CHECK, ELO

logger = logging.getLogger(__name__)


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        exclude = 'user', 'created', 'updated', 'active', 'elo',
        read_only_fields = ('name', 'bot_zip', 'plays_race', 'type')


class MatchSerializer(serializers.ModelSerializer):
    bot1 = BotSerializer(read_only=True)
    bot2 = BotSerializer(read_only=True)
    map = MapSerializer(read_only=True)

    class Meta:
        model = Match
        exclude = 'created',


class MatchViewSet(viewsets.GenericViewSet):
    """
    MatchViewSet implements a POST method with no field requirements, which will create a match and return the JSON.
    No reading of models is implemented.
    """
    serializer_class = MatchSerializer

    def create(self, request, *args, **kwargs):
        if Map.objects.count() == 0:
            raise APIException('There are no maps available for a match.')
        if Bot.objects.filter(active=True).count() <= 1:  # need at least 2 active bots for a match
            raise APIException('Not enough active bots available for a match.')

        match = Match.objects.create(map=Map.random())

        # Add participating bots
        bot1 = Bot.random_active()
        match.bot1 = Participant.objects.create(match=match, participant_number=1, bot=bot1).bot
        match.bot2 = Participant.objects.create(match=match, participant_number=2, bot=bot1.random_active_excluding_self()).bot

        serializer = self.get_serializer(match)
        return Response(serializer.data)


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """
    serializer_class = ResultSerializer

    def perform_create(self, serializer):
        result = serializer.save()
        self.adjust_elo(result)
        p1, p2 = result.get_participants()
        p1.update_resultant_elo()
        p2.update_resultant_elo()

        if ENABLE_ELO_SANITY_CHECK:
            # test here to check ELO total and ensure no corruption
            sumElo = Bot.objects.aggregate(Sum('elo'))
            if sumElo['elo__sum'] != ELO_START_VALUE * Bot.objects.all().count():
                raise EloSanityCheckException("ELO did not sum to expected value!")

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
