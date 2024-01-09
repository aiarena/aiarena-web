class BotNotInMatchException(Exception):
    pass


class BotAlreadyInMatchException(Exception):
    pass


class CompetitionPaused(Exception):
    def __init__(self):
        super().__init__("This competition is paused.")


class CompetitionClosing(Exception):
    def __init__(self):
        super().__init__("This competition is closing.")


class NoMaps(Exception):
    def __init__(self):
        super().__init__("There are no active maps available for a match.")


class NotEnoughAvailableBots(Exception):
    def __init__(self):
        super().__init__("Not enough available bots for a match. Wait until more bots become available.")


class MaxActiveRounds(Exception):
    def __init__(self):
        super().__init__("This competition has reached it's maximum active rounds.")
