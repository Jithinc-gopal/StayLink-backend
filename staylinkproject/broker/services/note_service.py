# broker/services/note_service.py
from django.shortcuts import get_object_or_404
from broker.models import BrokerNote


def get_all_notes(user, category=None, pinned_only=False, property_id=None):
    """
    Returns all notes for this broker.
    Multiple optional filters can be combined.

    category     → filter by category ('general', 'booking' etc.)
    pinned_only  → True → only return pinned notes
    property_id  → filter notes linked to a specific property
    """
    qs = BrokerNote.objects.filter(broker=user)

    if category:
        qs = qs.filter(category=category)

    if pinned_only:
        qs = qs.filter(is_pinned=True)

    if property_id:
        qs = qs.filter(related_property_id=property_id)

    return qs


def get_single_note(user, pk):
    """Returns a single note owned by this broker."""
    return get_object_or_404(BrokerNote, pk=pk, broker=user)


def create_note(user, validated_data):
    """Creates a new private note for this broker."""
    return BrokerNote.objects.create(broker=user, **validated_data)


def update_note(instance, validated_data):
    """Updates a note with new data."""
    for field, value in validated_data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def delete_note(instance):
    """Deletes a note."""
    instance.delete()


def toggle_pin(instance):
    """
    Toggles the pinned state of a note.
    Pinned notes appear at the top of the list.
    """
    instance.is_pinned = not instance.is_pinned
    instance.save()
    return instance