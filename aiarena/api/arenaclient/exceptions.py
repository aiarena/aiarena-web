from rest_framework.exceptions import APIException


class NoMaps(Exception):
    def __init__(self):
        super().__init__("There are no active maps available for a match.")


class NotEnoughAvailableBots(Exception):
    def __init__(self):
        super().__init__("Not enough available bots for a match. Wait until more bots become available.")


class MaxActiveRounds(Exception):
    def __init__(self):
        super().__init__("This competition has reached it's maximum active rounds.")


class LadderDisabled(APIException):
    status_code = 200
    default_detail = "The ladder is currently disabled."
    default_code = "ladder_disabled"


class CompetitionPaused(Exception):
    def __init__(self):
        super().__init__("This competition is paused.")


class CompetitionClosing(Exception):
    def __init__(self):
        super().__init__("This competition is closing.")


class NoGameForClient(APIException):
    status_code = 200
    default_detail = "No game available for client."
    default_code = "no_game_available"
