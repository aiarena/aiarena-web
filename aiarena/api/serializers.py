from django.contrib.auth import authenticate

from rest_framework import serializers

from aiarena.core.models import Bot, GameMode, Map


# From: https://www.guguweb.com/2022/01/23/django-rest-framework-authentication-the-easy-way/


class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """

    username = serializers.CharField(label="Username", write_only=True)
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get("request"), username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = "Access denied: wrong username or password."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code="authorization")
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs["user"] = user
        return attrs


class RequestMatchSerializer(serializers.Serializer):
    bot1 = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all())
    bot2 = serializers.PrimaryKeyRelatedField(queryset=Bot.objects.all())
    map = serializers.PrimaryKeyRelatedField(queryset=Map.objects.all(), required=False)
    game_mode = serializers.PrimaryKeyRelatedField(queryset=GameMode.objects.all(), required=False)
