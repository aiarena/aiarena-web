from rest_framework.exceptions import APIException


class EloSanityCheckException(APIException):
    pass


class NoMaps(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'There are no maps available for a match.'
    default_code = 'no_maps'


class NotEnoughActiveBots(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'Not enough active bots available for a match. Wait until more bots are activated.'
    default_code = 'not_enough_active_bots'


class NotEnoughAvailableBots(APIException):
    status_code = 409  # Conflict https://httpstatuses.com/409
    default_detail = 'Not enough available bots for a match. Wait until more bots become available.'
    default_code = 'not_enough_available_bots'
