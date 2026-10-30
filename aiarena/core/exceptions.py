class AIArenaException(Exception):
    pass


class BotNotInMatchException(AIArenaException):
    pass


class BotAlreadyInMatchException(AIArenaException):
    pass


class BotUploadsDisabled(AIArenaException):
    def __init__(self):
        super().__init__("Bot uploads are currently disabled.")


class CompetitionPaused(AIArenaException):
    def __init__(self):
        super().__init__("This competition is paused.")


class CompetitionClosing(AIArenaException):
    def __init__(self):
        super().__init__("This competition is closing.")


class CompetitionClosed(AIArenaException):
    def __init__(self):
        super().__init__("This competition is closed.")


class CompetitionDeletionNotAllowed(AIArenaException):
    def __init__(self, competition):
        super().__init__(
            f"Competition {competition.id} ({competition.name}) does not allow deletion. "
            f"Set its deletion_allowed flag first if you really intend to delete it."
        )


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
