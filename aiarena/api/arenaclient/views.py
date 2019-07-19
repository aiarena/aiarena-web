import logging
from wsgiref.util import FileWrapper

from django.http import HttpResponse
from rest_framework import viewsets, serializers, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.fields import FileField, FloatField
from rest_framework.response import Response
from rest_framework.reverse import reverse

from aiarena.core.exceptions import BotNotInMatchException
from aiarena.core.models import Bot, Map, Match, Participant, Result

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
        fields = (
            'id', 'name', 'game_display_id', 'bot_zip', 'bot_zip_md5hash', 'bot_data', 'bot_data_md5hash', 'plays_race',
            'type')


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
        match = Match.start_next_match(request.user)

        match.bot1 = Participant.objects.get(match_id=match.id, participant_number=1).bot
        match.bot2 = Participant.objects.get(match_id=match.id, participant_number=2).bot

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
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    bot1_log = FileField(required=False)
    bot2_log = FileField(required=False)

    bot1_avg_step_time = FloatField(required=False)
    bot2_avg_step_time = FloatField(required=False)

    def validate(self, attrs):
        # temporarily remove the extra fields so they don't cause validation failure
        modified_attrs = attrs.copy()
        if 'bot1_data' in attrs:
            modified_attrs.pop('bot1_data')
        if 'bot2_data' in attrs:
            modified_attrs.pop('bot2_data')
        if 'bot1_log' in attrs:
            modified_attrs.pop('bot1_log')
        if 'bot2_log' in attrs:
            modified_attrs.pop('bot2_log')
        if 'bot1_avg_step_time' in attrs:
            modified_attrs.pop('bot1_avg_step_time')
        if 'bot2_avg_step_time' in attrs:
            modified_attrs.pop('bot2_avg_step_time')
        instance = ResultSerializer.Meta.model(**modified_attrs)

        instance.clean()  # enforce model validation because the result model has some custom checks
        return attrs

    class Meta:
        model = Result
        fields = 'type', 'replay_file', 'game_steps', 'submitted_by', 'match', 'bot1_data',\
                 'bot2_data', 'bot1_log', 'bot2_log', 'bot1_avg_step_time', 'bot2_avg_step_time'


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """
    serializer_class = ResultSerializer

    # todo: avoid results being logged against matches not owned by the submitter
    def perform_create(self, serializer):
        # pop extra fields so they don't interfere with saving the result
        # todo: override serializer save method instead of having to do this?
        bot1_data = None
        bot2_data = None
        bot1_log = None
        bot2_log = None
        bot1_avg_step_time = None
        bot2_avg_step_time = None
        if 'bot1_data' in serializer.validated_data:
            bot1_data = serializer.validated_data.pop('bot1_data')
        if 'bot2_data' in serializer.validated_data:
            bot2_data = serializer.validated_data.pop('bot2_data')
        if 'bot1_log' in serializer.validated_data:
            bot1_log = serializer.validated_data.pop('bot1_log')
        if 'bot2_log' in serializer.validated_data:
            bot2_log = serializer.validated_data.pop('bot2_log')
        if 'bot1_avg_step_time' in serializer.validated_data:
            bot1_avg_step_time = serializer.validated_data.pop('bot1_avg_step_time')
        if 'bot2_avg_step_time' in serializer.validated_data:
            bot2_avg_step_time = serializer.validated_data.pop('bot2_avg_step_time')

        try:
            result = serializer.save()
            result.finalize_submission(bot1_data, bot2_data, bot1_log, bot2_log, bot1_avg_step_time, bot2_avg_step_time)
        except BotNotInMatchException:
            raise APIException('Unable to log result - one of the bots is not listed as in this match.')
