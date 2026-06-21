# broker/services/property_service.py
from django.shortcuts import get_object_or_404
from broker.models import (
    BrokerUnlistedProperty,
    BrokerBookingRecord,
)


# ============================================================
# UNLISTED PROPERTY SERVICES
# ============================================================

def get_all_properties(user, active_filter=None):
    """
    Returns all unlisted properties for this broker.
    active_filter: 'true' → only active
                   'false' → only inactive
                   None → all
    """
    qs = BrokerUnlistedProperty.objects.filter(broker=user)

    if active_filter == 'true':
        qs = qs.filter(is_active=True)
    elif active_filter == 'false':
        qs = qs.filter(is_active=False)

    return qs


def get_single_property(user, pk):
    """
    Returns a single unlisted property that belongs to this broker.
    Returns 404 if not found or not owned by this broker.
    """
    return get_object_or_404(
        BrokerUnlistedProperty,
        pk=pk,
        broker=user
    )


def create_property(user, validated_data):
    """
    Creates a new unlisted property for this broker.
    validated_data comes from BrokerUnlistedPropertySerializer.
    """
    return BrokerUnlistedProperty.objects.create(
        broker=user,
        **validated_data
    )


def update_property(instance, validated_data):
    """
    Updates fields on an existing unlisted property.
    Only updates fields that were passed (partial update).
    """
    for field, value in validated_data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def delete_property(instance):
    """
    Deletes an unlisted property.
    All related booking records are also deleted (CASCADE).
    """
    instance.delete()


# ============================================================
# BOOKING RECORD SERVICES
# ============================================================

def get_all_booking_records(user, property_id=None, status=None):
    """
    Returns booking records for this broker.
    Optional filters:
      property_id → only bookings for that property
      status      → filter by status (pending/confirmed/completed/cancelled)
    """
    qs = BrokerBookingRecord.objects.filter(
        broker=user
    ).select_related('unlisted_property')

    if property_id:
        qs = qs.filter(unlisted_property_id=property_id)
    if status:
        qs = qs.filter(status=status)

    return qs


def get_single_booking_record(user, pk):
    """
    Returns a single booking record owned by this broker.
    """
    return get_object_or_404(
        BrokerBookingRecord,
        pk=pk,
        broker=user
    )


def create_booking_record(user, validated_data):
    """
    Creates a manual booking record.
    Auto-calculates commission_amount from the property's
    commission_percentage and the total_amount.

    Formula: commission = total_amount × (commission_percentage / 100)
    """
    unlisted_property = validated_data['unlisted_property']
    total = validated_data.get('total_amount', 0)
    commission_pct = unlisted_property.commission_percentage

    commission_amount = total * commission_pct / 100

    return BrokerBookingRecord.objects.create(
        broker=user,
        commission_amount=commission_amount,
        **validated_data
    )


def update_booking_record(instance, validated_data):
    """
    Updates a booking record.
    If total_amount changes, recalculates commission_amount.
    """
    # Recalculate commission if total_amount is being updated
    if 'total_amount' in validated_data:
        commission_pct = instance.unlisted_property.commission_percentage
        validated_data['commission_amount'] = (
            validated_data['total_amount'] * commission_pct / 100
        )

    for field, value in validated_data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def delete_booking_record(instance):
    """Deletes a booking record."""
    instance.delete() 