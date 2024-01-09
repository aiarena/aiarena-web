from rest_framework.exceptions import APIException


class LadderDisabled(APIException):
    status_code = 200
    default_detail = "The ladder is currently disabled."
    default_code = "ladder_disabled"


class NoGameForClient(APIException):
    status_code = 200
    default_detail = "No game available for client."
    default_code = "no_game_available"
