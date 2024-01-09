from aiarena.api.arenaclient.common.serializers import MapSerializer, MatchSerializer


class V2MapSerializer(MapSerializer):
    class Meta(MapSerializer.Meta):
        fields = ["name", "file", "file_hash"]


class V2MatchSerializer(MatchSerializer):
    map = V2MapSerializer()
