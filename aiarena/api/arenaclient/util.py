from aiarena.core.models import MatchParticipation


def get_winner_loser(result_type, bot1, bot2):
    if result_type in ('Player1Win', 'Player2Crash', 'Player2TimeOut', 'Player2Surrender'):
        return bot1, bot2
    elif result_type in ('Player2Win', 'Player1Crash', 'Player1TimeOut', 'Player1Surrender'):
        return bot2, bot1
    else:
        raise Exception('There was no winner or loser for this match.')


def select_competition_participant_for_update(match_id, participant_number):
    match_participation = MatchParticipation.objects.get(match_id=match_id, participant_number=participant_number)
    obj = match_participation.__class__.objects.select_related('match', 'match__round',
                                                               'match__round__competition').get(
        id=match_participation.id)
    return obj.match.round.competition.participations.select_for_update().get(bot_id=match_participation.bot_id)


def get_competition_participant_bot_id(match_id, participant_number):
    match_participation = MatchParticipation.objects.get(match_id=match_id, participant_number=participant_number)
    return match_participation.__class__.objects.get(id=match_participation.id).bot_id


def apply_elo_delta(delta, p1, p2):
    delta = int(round(delta))
    p1.elo += delta
    p2.elo -= delta
