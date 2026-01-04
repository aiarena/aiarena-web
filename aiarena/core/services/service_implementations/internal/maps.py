from aiarena.core.models import Competition, Map, MapPool
from aiarena.core.models.game_mode import GameMode


class Maps:
    @staticmethod
    def random_of_competition(competition: Competition):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(competition=competition).order_by("?").first()

    @staticmethod
    def random_of_game_mode(game_mode: GameMode):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(game_mode=game_mode).order_by("?").first()

    @staticmethod
    def random_from_map_pool(map_pool: MapPool):
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Map.objects.filter(map_pools__in=[map_pool]).order_by("?").first()
