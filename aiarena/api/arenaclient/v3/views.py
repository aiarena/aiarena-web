from aiarena.api.arenaclient.v2.views import V2MatchViewSet, V2ResultViewSet, V2SetArenaClientStatusViewSet
from aiarena.api.arenaclient.v3.serializers import V3MatchSerializer


class V3MatchViewSet(V2MatchViewSet):
    """
    The V3MatchSerializer replaces the md5hash retrieval to instead reference the S3 etag, if available.
    """

    serializer_class = V3MatchSerializer


class V3ResultViewSet(V2ResultViewSet):
    pass  # No changes


class V3SetArenaClientStatusViewSet(V2SetArenaClientStatusViewSet):
    pass  # No changes
