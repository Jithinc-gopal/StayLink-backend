from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.serializers import BrokerReviewSerializer
from broker.services import review_service


class BrokerReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, broker_id):
        reviews = review_service.get_broker_reviews(
            broker_id
        )

        serializer = BrokerReviewSerializer(
            reviews,
            many=True
        )

        return Response(serializer.data)

    def post(self, request, broker_id):
        serializer = BrokerReviewSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        try:
            review = review_service.create_review(
                broker_id,
                request.user,
                serializer.validated_data
            )

            return Response(
                {
                    "message": "Review submitted",
                    "data": BrokerReviewSerializer(review).data
                },
                status=201
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )