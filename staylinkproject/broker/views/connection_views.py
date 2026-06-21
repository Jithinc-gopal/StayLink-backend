from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.permissions import IsApprovedBroker
from broker.serializers import (
    BrokerConnectionSerializer,
    BrokerProfilePublicSerializer,
)
from broker.services import connection_service


class BrokerConnectionListView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        status_filter = request.query_params.get("status")

        connections = connection_service.get_connections(
            request.user,
            status_filter
        )

        serializer = BrokerConnectionSerializer(
            connections,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = BrokerConnectionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            connection = connection_service.send_connection_request(
                request.user,
                serializer.validated_data
            )

            return Response(
                {
                    "message": "Connection request sent",
                    "data": BrokerConnectionSerializer(connection).data
                },
                status=201
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )


class BrokerConnectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def delete(self, request, pk):
        connection_service.delete_connection(
            request.user,
            pk
        )

        return Response(
            {"message": "Connection removed"}
        )


class ConnectionRequestResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = connection_service.get_incoming_requests(
            request.user
        )

        serializer = BrokerConnectionSerializer(
            requests,
            many=True
        )

        return Response(serializer.data)

    def put(self, request, pk):
        action = request.data.get("action")

        try:
            connection = connection_service.respond_to_request(
                request.user,
                pk,
                action
            )

            return Response({
                "message": f"Connection {connection.status}"
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )


class PublicBrokerListView(APIView):
    permission_classes = []

    def get(self, request):
        brokers = connection_service.get_public_broker_list()

        serializer = BrokerProfilePublicSerializer(
            brokers,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)