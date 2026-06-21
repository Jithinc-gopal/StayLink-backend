# broker/views/note_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from broker.permissions import IsApprovedBroker
from broker.serializers import BrokerNoteSerializer
from broker.services import note_service


class BrokerNoteListView(APIView):
    """
    GET  → List notes (optional ?category=&pinned=true&property_id=)
    POST → Create a new note
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request):
        notes = note_service.get_all_notes(
            user=request.user,
            category=request.query_params.get('category'),
            pinned_only=request.query_params.get('pinned') == 'true',
            property_id=request.query_params.get('property_id')
        )
        serializer = BrokerNoteSerializer(notes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrokerNoteSerializer(data=request.data)
        if serializer.is_valid():
            note = note_service.create_note(
                request.user,
                serializer.validated_data
            )
            return Response(
                {
                    "message": "Note created",
                    "data": BrokerNoteSerializer(note).data
                },
                status=201
            )
        return Response(serializer.errors, status=400)


class BrokerNoteDetailView(APIView):
    """
    GET    → View single note
    PUT    → Edit note
    DELETE → Delete note
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def get(self, request, pk):
        note = note_service.get_single_note(request.user, pk)
        return Response(BrokerNoteSerializer(note).data)

    def put(self, request, pk):
        note = note_service.get_single_note(request.user, pk)
        serializer = BrokerNoteSerializer(
            note,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            updated = note_service.update_note(
                note,
                serializer.validated_data
            )
            return Response({
                "message": "Note updated",
                "data": BrokerNoteSerializer(updated).data
            })
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        note = note_service.get_single_note(request.user, pk)
        note_service.delete_note(note)
        return Response({"message": "Note deleted"})


class BrokerNoteTogglePinView(APIView):
    """
    PUT → Toggle pin status of a note
    Pinned notes appear at the top of the list.
    """
    permission_classes = [IsAuthenticated, IsApprovedBroker]

    def put(self, request, pk):
        note = note_service.get_single_note(request.user, pk)
        updated = note_service.toggle_pin(note)
        return Response({
            "message": (
                "Note pinned" if updated.is_pinned
                else "Note unpinned"
            ),
            "is_pinned": updated.is_pinned
        })