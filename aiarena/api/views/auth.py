from django.contrib.auth import login, logout

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from aiarena.api.views import serializers as api_serializers


class AuthViewSet(ViewSet):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "Current user information",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "current_user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
        }
    )
    def list(self, request):
        current_user = {"id": request.user.id, "username": request.user.username} if request.user.id else None

        return Response({"current_user": current_user}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=api_serializers.LoginSerializer,
        responses={
            202: "Accepted",
            400: "Bad Request",
        },
    )
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = api_serializers.LoginSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        responses={
            204: "No Content",
        }
    )
    @action(detail=False, methods=["post"])
    def logout(self, request):
        logout(request)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
