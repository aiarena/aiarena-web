from rest_framework.exceptions import APIException


class EloSanityCheckException(APIException):
    pass


class NoMaps(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'There are no active maps available for a match.'
    default_code = 'no_maps'


class NotEnoughActiveBots(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'Not enough active bots available for a match. Wait until more bots are activated.'
    default_code = 'not_enough_active_bots'


class NotEnoughAvailableBots(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'Not enough available bots for a match. Wait until more bots become available.'
    default_code = 'not_enough_available_bots'


class MaxActiveRounds(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'There are available bots, but the ladder has reached the maximum active rounds allowed and ' \
                     'serving a new match would require generating a new one. Please wait until matches from current ' \
                     'rounds become available.'
    default_code = 'max_active_rounds'


class LadderDisabled(APIException):
    status_code = 503  # Service Unavailable https://httpstatuses.com/503
    default_detail = 'The ladder is currently disabled.'
    default_code = 'ladder_disabled'
