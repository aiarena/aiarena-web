class AIArenaException(Exception):
    pass


class BotNotInMatchException(AIArenaException):
    pass


class BotAlreadyInMatchException(AIArenaException):
    pass


class CompetitionPaused(AIArenaException):
    def __init__(self):
        super().__init__("This competition is paused.")


class CompetitionClosing(AIArenaException):
    def __init__(self):
        super().__init__("This competition is closing.")


class CompetitionClosed(AIArenaException):
    def __init__(self):
        super().__init__("This competition is closed.")


class NoMaps(AIArenaException):
    def __init__(self):
        super().__init__("There are no active maps available for a match.")


class NotEnoughAvailableBots(AIArenaException):
    def __init__(self):
        super().__init__("Not enough available bots for a match. Wait until more bots become available.")


class MaxActiveRounds(AIArenaException):
    def __init__(self):
        super().__init__("This competition has reached it's maximum active rounds.")


class MatchRequestException(AIArenaException):
    def __init__(self, message):
        super().__init__(message)
