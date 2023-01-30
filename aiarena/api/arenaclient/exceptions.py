from rest_framework.exceptions import APIException


class EloSanityCheckException(APIException):
    pass


class NoMaps(APIException):
    status_code = 200
    default_detail = 'There are no active maps available for a match.'
    default_code = 'no_maps'


class NotEnoughActiveBots(APIException):
    status_code = 200
    default_detail = 'Not enough active bots available for a match. Wait until more bots are activated.'
    default_code = 'not_enough_active_bots'


class NotEnoughAvailableBots(APIException):
    status_code = 200
    default_detail = 'Not enough available bots for a match. Wait until more bots become available.'
    default_code = 'not_enough_available_bots'


class MaxActiveRounds(APIException):
    status_code = 200
    default_detail = 'This competition has reached it\'s maximum active rounds.'
    default_code = 'max_active_rounds'


class LadderDisabled(APIException):
    status_code = 200
    default_detail = 'The ladder is currently disabled.'
    default_code = 'ladder_disabled'


class CompetitionPaused(APIException):
    status_code = 200
    default_detail = 'The competition is paused.'
    default_code = 'competition_paused'


class CompetitionClosing(APIException):
    status_code = 200
    default_detail = 'This competition is closing.'
    default_code = 'competition_closing'

class NoGameForClient(APIException):
    status_code = 200
    default_detail = 'No game available for client.'
    default_code = 'no_game_available'
