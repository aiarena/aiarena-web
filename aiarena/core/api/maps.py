from aiarena.core.models import Competition, Map
from aiarena.core.models.game_type import GameMode


class Maps:
    @staticmethod
    def random_of_competition(competition: Competition):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(competition=competition).order_by('?').first()

    @staticmethod
    def random_of_game_mode(game_mode: GameMode):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(game_mode=game_mode).order_by('?').first()
