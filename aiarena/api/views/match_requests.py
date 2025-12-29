from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from aiarena.api.views.serializers import RequestMatchSerializer
from aiarena.core.services import match_requests, supporter_benefits


class MatchRequestsViewSet(viewsets.ViewSet):
    """
    Match request view
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        method="post",
        request_body=RequestMatchSerializer,
        responses={
            201: openapi.Response(
                "Match requested successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "match_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    @action(detail=False, methods=["post"])
    def request_single(self, request):
        """
        Request a match between two bots.
        """

        allowed, reject_message = supporter_benefits.can_request_match_via_api(request.user)
        if not allowed:
            return Response({"message": reject_message}, status=status.HTTP_403_FORBIDDEN)

        serializer = RequestMatchSerializer(data=request.data)
        if serializer.is_valid():
            bot1 = serializer.validated_data["bot1"]
            bot2 = serializer.validated_data["bot2"]
            map_instance = serializer.validated_data.get("map")

            try:
                match = match_requests.request_match(request.user, bot1, bot2, map_instance)
                return Response(
                    {"message": "Match requested successfully", "match_id": match.id}, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
