from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from aiarena.core.models import Bot, Map, Match, Participant, Result


# todo: restrict aiarena-client specific endpoints to staff only

class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'


class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class MapViewSet(viewsets.ModelViewSet):
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
    def next(self, request, *args, **kwargs):
        # todo: account for No maps present
        # todo: account for No Bots present
        # todo: transaction
        match = Match.objects.create(map=Map.random())

        # Add participating bots
        bot1 = Bot.random()
        Participant.objects.create(match=match, participant_number=1, bot=bot1)
        Participant.objects.create(match=match, participant_number=2, bot=bot1.random_excluding_self())

        serializer = self.get_serializer(match)
        return Response(serializer.data)


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
