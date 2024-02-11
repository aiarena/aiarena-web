from rest_framework import serializers

from aiarena.api.arenaclient.common.serializers import BotSerializer
from aiarena.api.arenaclient.common.util import obtain_s3_filehash_or_default
from aiarena.api.arenaclient.v2.serializers import V2MatchSerializer


class V3BotSerializer(BotSerializer):
    """
    This serializer overrides the md5hash fields to return the S3 etag instead of the local storage md5hash.
    This is to enable a migration path which will culminate in the removal of the md5hash fields.
    """

    bot_zip_md5hash = serializers.SerializerMethodField()
    bot_data_md5hash = serializers.SerializerMethodField()

    def get_bot_zip_md5hash(self, obj):
        return obtain_s3_filehash_or_default(obj.bot_zip, default=obj.bot_zip_md5hash)

    def get_bot_data_md5hash(self, obj):
        return obtain_s3_filehash_or_default(obj.bot_data, default=obj.bot_zip_md5hash)


class V3MatchSerializer(V2MatchSerializer):
    bot1 = V3BotSerializer(read_only=True)
    bot2 = V3BotSerializer(read_only=True)
