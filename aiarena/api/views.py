from django.db import transaction
from django.db.models import Sum
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from aiarena.api.exceptions import EloSanityCheckException
from aiarena.core.models import Bot, Map, Match, Participant, Result
from aiarena.core.utils import calculate_elo_delta
from aiarena.settings import ELO_START_VALUE, ENABLE_ELO_SANITY_CHECK


class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        exclude = 'user',


class BotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Map.objects.all()
    serializer_class = MapSerializer


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    @action(detail=False, methods=['GET'], name='Create next match')
    @transaction.atomic
    def next(self, request, *args, **kwargs):
        if Map.objects.count() == 0:
            raise APIException('There are no maps available for a match.')
        if Bot.objects.filter(active=True).count() <= 1:  # need at least 2 active bots for a match
            raise APIException('Not enough active bots available for a match.')

        match = Match.objects.create(map=Map.random())

        # Add participating bots
        bot1 = Bot.random_active()
        Participant.objects.create(match=match, participant_number=1, bot=bot1)
        Participant.objects.create(match=match, participant_number=2, bot=bot1.random_active_excluding_self())

        serializer = self.get_serializer(match)
        return Response(serializer.data)


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class ParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filterset_fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def perform_create(self, serializer):
        self.adjust_elo(serializer.save())

        if ENABLE_ELO_SANITY_CHECK:
            # test here to check ELO total and ensure no corruption
            sumElo = Bot.objects.aggregate(Sum('elo'))
            if sumElo['elo__sum'] != ELO_START_VALUE * Bot.objects.all().count():
                raise EloSanityCheckException("ELO did not sum to expected value!")

    # todo: write a test which ensures this actually works properly
    def adjust_elo(self, result):
        if result.has_winner():
            winner, loser = result.get_winner_loser_bots()
            self.apply_elo_delta(calculate_elo_delta(winner.elo, loser.elo, 1.0), winner, loser)
        elif result.type == 'Tie':
            first, second = result.get_participant_bots()
            self.apply_elo_delta(calculate_elo_delta(first.elo, second.elo, 0.5), first, second)

    def apply_elo_delta(self, delta, bot1, bot2):
        delta = int(round(delta))
        bot1.elo += delta
        bot1.save()
        bot2.elo -= delta
        bot2.save()
