from ..common.views import MatchViewSet, ResultViewSet, SetArenaClientStatusViewSet
from .serializers import V2MatchSerializer


class V2MatchViewSet(MatchViewSet):
    serializer_class = V2MatchSerializer


class V2ResultViewSet(ResultViewSet):
    pass


class V2SetArenaClientStatusViewSet(SetArenaClientStatusViewSet):
    pass
