from django.db import transaction
from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from aiarena.core.models import Bot, Map, Match, Participant, Result


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

    def adjust_elo(self, result):
        if result.winner:
            winner, loser = result.get_winner_loser_bots()
            # todo: assign elo
            winner.elo += 1
            winner.save()
            loser.elo -= 1
            loser.save()
        # todo: adjust on tie?
