import logging
from wsgiref.util import FileWrapper

from constance import config
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponse
from rest_framework import viewsets, serializers, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.fields import FileField, FloatField
from rest_framework.response import Response
from rest_framework.reverse import reverse

from aiarena import settings
from aiarena.api.arenaclient.exceptions import LadderDisabled
from aiarena.core.events import EVENT_MANAGER
from aiarena.core.permissions import IsArenaClientOrAdminUser
from aiarena.core.models import Bot, Map, Match, MatchParticipation, Result, SeasonParticipation
from aiarena.core.validators import validate_not_inf, validate_not_nan
from aiarena.core.events import MatchResultReceivedEvent
from aiarena.core.api import Bots, Matches

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
        p = MatchParticipation.objects.get(bot=obj, match=obj.current_match)
        return reverse('match-download-zip', kwargs={'pk': obj.current_match.pk, 'p_num': p.participant_number},
                       request=self.context['request'])

    def get_bot_data(self, obj):
        p = MatchParticipation.objects.get(bot=obj, match=obj.current_match)
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
    permission_classes = [IsArenaClientOrAdminUser]

    def create_new_match(self, requesting_user):
        match = Matches.start_next_match(requesting_user)

        match.bot1 = MatchParticipation.objects.get(match_id=match.id, participant_number=1).bot
        match.bot2 = MatchParticipation.objects.get(match_id=match.id, participant_number=2).bot

        serializer = self.get_serializer(match)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        if config.LADDER_ENABLED:
            if config.REISSUE_UNFINISHED_MATCHES:
                # Check for any unfinished matches assigned to this user. If any are present, return that.
                unfinished_matches = Match.objects.filter(started__isnull=False, assigned_to=request.user,
                                                          result__isnull=True).order_by(F('round_id').asc())
                if unfinished_matches.count() > 0:
                    match = unfinished_matches[0]  # todo: re-set started time?

                    match.bot1 = MatchParticipation.objects.get(match_id=match.id, participant_number=1).bot
                    match.bot2 = MatchParticipation.objects.get(match_id=match.id, participant_number=2).bot

                    serializer = self.get_serializer(match)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return self.create_new_match(request.user)
            else:
                return self.create_new_match(request.user)
        else:
            raise LadderDisabled()

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s zip file', url_path='(?P<p_num>\d+)/zip')
    def download_zip(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_zip), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}.zip"'.format(p.bot.name)
        return response

    # todo: check match is in progress/bot is in this match
    @action(detail=True, methods=['GET'], name='Download a participant\'s data file', url_path='(?P<p_num>\d+)/data')
    def download_data(self, request, *args, **kwargs):
        p = MatchParticipation.objects.get(match=kwargs['pk'], participant_number=kwargs['p_num'])
        response = HttpResponse(FileWrapper(p.bot.bot_data), content_type='application/zip')
        response['Content-Disposition'] = 'inline; filename="{0}_data.zip"'.format(p.bot.name)
        return response


class SubmitResultResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = 'match', 'type', 'replay_file', 'game_steps', 'submitted_by', 'arenaclient_log'


class SubmitResultBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = 'bot_data', 'in_match', 'current_match'


class SubmitResultParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchParticipation
        fields = 'avg_step_time', 'match_log', 'result', 'result_cause'


# Front facing serializer used by the view. Combines the other serializers together.
class SubmitResultCombinedSerializer(serializers.Serializer):
    # Result
    match = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Result.TYPES)
    replay_file = serializers.FileField(required=False)
    game_steps = serializers.IntegerField()
    submitted_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    arenaclient_log = FileField(required=False)
    # Bot
    bot1_data = FileField(required=False)
    bot2_data = FileField(required=False)
    # Participant
    bot1_log = FileField(required=False)
    bot2_log = FileField(required=False)
    bot1_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])
    bot2_avg_step_time = FloatField(required=False, validators=[validate_not_nan, validate_not_inf])


class ResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ResultViewSet implements a POST method to log a result.
    No reading of models is implemented.
    """
    serializer_class = SubmitResultCombinedSerializer
    permission_classes = [IsArenaClientOrAdminUser]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        if config.LADDER_ENABLED:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if config.ARENACLIENT_DEBUG_ENABLED:  # todo: make this an INFO or DEBUG level log?
                logger.critical(
                    "Bot1 avg_step_size: {0}".format(serializer.validated_data.get('bot1_avg_step_time')))
                logger.critical(
                    "Bot2 avg_step_size: {0}".format(serializer.validated_data.get('bot2_avg_step_time')))

            # validate result
            result = SubmitResultResultSerializer(data={'match': serializer.validated_data['match'],
                                                        'type': serializer.validated_data['type'],
                                                        'replay_file': serializer.validated_data.get('replay_file'),
                                                        'game_steps': serializer.validated_data['game_steps'],
                                                        'submitted_by': serializer.validated_data['submitted_by'].pk,
                                                        'arenaclient_log': serializer.validated_data.get(
                                                            'arenaclient_log')})
            result.is_valid(raise_exception=True)

            # validate participants
            p1Instance = MatchParticipation.objects.get(match_id=serializer.validated_data['match'],
                                                        participant_number=1)
            participant1 = SubmitResultParticipationSerializer(instance=p1Instance, data={
                'avg_step_time': serializer.validated_data.get('bot1_avg_step_time'),
                'match_log': serializer.validated_data.get('bot1_log'),
                'result': p1Instance.calculate_relative_result(serializer.validated_data['type']),
                'result_cause': p1Instance.calculate_relative_result_cause(serializer.validated_data['type'])},
                                                               partial=True)
            participant1.is_valid(raise_exception=True)
            p2Instance = MatchParticipation.objects.get(match_id=serializer.validated_data['match'],
                                                        participant_number=2)
            participant2 = SubmitResultParticipationSerializer(instance=p2Instance, data={
                'avg_step_time': serializer.validated_data.get('bot2_avg_step_time'),
                'match_log': serializer.validated_data.get('bot2_log'),
                'result': p2Instance.calculate_relative_result(serializer.validated_data['type']),
                'result_cause': p2Instance.calculate_relative_result_cause(serializer.validated_data['type'])},
                                                               partial=True)
            participant2.is_valid(raise_exception=True)

            # validate bots
            match = result.validated_data['match']

            if p1Instance.bot.current_match_id != match.id:
                raise APIException('Unable to log result: Bot {0} is not currently in this match!'
                                   .format(p1Instance.bot.name))
            bot1_data = serializer.validated_data.get('bot1_data')
            bot1_dict = {'in_match': False, 'current_match': None}
            # if we set the bot data key to anything, it will overwrite the existing bot data
            # so only include bot1_data if it isn't none
            # Also don't update bot data if it's a requested match.
            if bot1_data is not None and not match.is_requested:
                bot1_dict['bot_data'] = bot1_data
            bot1 = SubmitResultBotSerializer(instance=p1Instance.bot,
                                             data=bot1_dict, partial=True)
            bot1.is_valid(raise_exception=True)

            if p2Instance.bot.current_match_id != match.id:
                raise APIException('Unable to log result: Bot {0} is not currently in this match!'
                                   .format(p2Instance.bot.name))
            bot2_data = serializer.validated_data.get('bot2_data')
            bot2_dict = {'in_match': False, 'current_match': None}
            # if we set the bot data key to anything, it will overwrite the existing bot data
            # so only include bot2_data if it isn't none
            # Also don't update bot data if it's a requested match.
            if bot2_data is not None and not match.is_requested:
                bot2_dict['bot_data'] = bot2_data
            bot2 = SubmitResultBotSerializer(instance=p2Instance.bot,
                                             data=bot2_dict, partial=True)
            bot2.is_valid(raise_exception=True)

            # save models
            result = result.save()
            participant1 = participant1.save()
            participant2 = participant2.save()
            bot1.save()
            bot2.save()

            # Only do these actions if the match is part of a round
            if result.match.round is not None:
                result.match.round.update_if_completed()

                # Update and record ELO figures
                p1_initial_elo, p2_initial_elo = result.get_initial_elos()
                result.adjust_elo()

                # Calculate the change in ELO
                # the bot elos have changed so refresh them
                # todo: instead of having to refresh, return data from adjust_elo and apply it here
                sp1, sp2 = result.get_season_participants()
                participant1.resultant_elo = sp1.elo
                participant2.resultant_elo = sp2.elo
                participant1.elo_change = participant1.resultant_elo - p1_initial_elo
                participant2.elo_change = participant2.resultant_elo - p2_initial_elo
                participant1.save()
                participant2.save()

                if settings.ENABLE_ELO_SANITY_CHECK:
                    # test here to check ELO total and ensure no corruption
                    expectedEloSum = settings.ELO_START_VALUE * SeasonParticipation.objects.filter(season=result.match.round.season).count()
                    actualEloSum = SeasonParticipation.objects.filter(season=result.match.round.season).aggregate(
                        Sum('elo'))

                    if actualEloSum['elo__sum'] != expectedEloSum:
                        logger.critical(
                            "ELO sum of {0} did not match expected value of {1} upon submission of result {2}".format(
                                actualEloSum['elo__sum'], expectedEloSum, result.id))

                if result.is_crash_or_timeout():
                    run_consecutive_crashes_check(result.get_causing_participant_of_crash_or_timeout_result())

            EVENT_MANAGER.broadcast_event(MatchResultReceivedEvent(result))

            headers = self.get_success_headers(serializer.data)
            return Response({'result_id': result.id}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            raise LadderDisabled()

    # todo: use a model form
    # todo: avoid results being logged against matches not owned by the submitter


def run_consecutive_crashes_check(triggering_participant: MatchParticipation):
    """
    Checks to see whether the last X results for a participant are crashes and, if so, disables the bot
    and sends an alert to the bot author
    :param triggering_participant: The participant who triggered this check and whose bot we should run the check for.
    :return:
    """

    if config.BOT_CONSECUTIVE_CRASH_LIMIT < 1:
        return  # Check is disabled

    if not triggering_participant.bot.active:
        return  # No use running the check - bot is already inactive.

    # Get recent match participation records for this bot
    recent_participations = MatchParticipation.objects.filter(bot=triggering_participant.bot,
                                                              match__result__isnull=False).order_by(
        '-match__result__created')[:config.BOT_CONSECUTIVE_CRASH_LIMIT]

    # if there's not enough participations yet, then exit without action
    if recent_participations.count() < config.BOT_CONSECUTIVE_CRASH_LIMIT:
        return

    # if any of the previous results weren't a crash, then exit without action
    for recent_participation in recent_participations:
        if not recent_participation.crashed:
            return

    # If we get to here, all the results were crashes, so take action
    Bots.disable_and_send_crash_alert(triggering_participant.bot)
