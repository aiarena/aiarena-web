from aiarena.core.models import Bot
from rest_framework import viewsets, serializers

# todo: restrict aiarena-client specific endpoints to staff only

class BotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = '__all__'


class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
