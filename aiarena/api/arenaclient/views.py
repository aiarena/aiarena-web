import logging

from django.db.models import Sum
from rest_framework import viewsets, serializers, mixins
from rest_framework.exceptions import APIException
from rest_framework.fields import FileField
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

        # todo: add in game timeout
        if Bot.objects.filter(active=True, in_match=False).count() <= 1:  # need at least 2 bots that aren't in game
            raise APIException('Not enough available bots available for a match.')

        match = Match.objects.create(map=Map.random())

        # Add participating bots
        bot1 = Bot.get_random_available()
        bot2 = bot1.get_random_available_excluding_self()

        # create match participants
        Participant.objects.create(match=match, participant_number=1, bot=bot1)
        Participant.objects.create(match=match, participant_number=2, bot=bot2)

        # mark bots as in match
        bot1.in_match = True
        bot1.save()
        bot2.in_match = True
        bot2.save()

        # return bot data along with the match
        match.bot1 = bot1
        match.bot2 = bot2

        serializer = self.get_serializer(match)
        return Response(serializer.data)


class ResultSerializer(serializers.ModelSerializer):
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)

    def validate(self, attrs):
        instance = ResultSerializer.Meta.model(**attrs)
        instance.clean()  # enforce model validation
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
        self.adjust_elo(result)
        p1, p2 = result.get_participants()
        p1.update_resultant_elo()
        p2.update_resultant_elo()

        if ENABLE_ELO_SANITY_CHECK:
            # test here to check ELO total and ensure no corruption
            sumElo = Bot.objects.aggregate(Sum('elo'))
            if sumElo['elo__sum'] != ELO_START_VALUE * Bot.objects.all().count():
                raise EloSanityCheckException("ELO did not sum to expected value!")

        bot1 = serializer.validated_data['match'].participant_set.get(participant_number=1).bot
        bot2 = serializer.validated_data['match'].participant_set.get(participant_number=2).bot

        # save bot datas
        if process_bot1_data:
            bot1.bot_data = bot1_data
            bot1.save()

        if process_bot2_data:
            bot2.bot_data = bot2_data
            bot2.save()

        if bot1.in_match:
            bot1.in_match = False
            bot2.save()
        else:
            logger.warning('A result was submitted involving a bot not marked as "in_match"')

        if bot2.in_match:
            bot2.in_match = False
            bot2.save()
        else:
            logger.warning('A result was submitted involving a bot not marked as "in_match"')

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
