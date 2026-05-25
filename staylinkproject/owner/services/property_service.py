from django.shortcuts import get_object_or_404
from django.db import transaction
from ..models import (
    Property,
    PropertyImage,
    PropertyAmenity,
    Amenity
)


# =========================================
# CREATE PROPERTY
# =========================================

@transaction.atomic
def create_property_service(
    user,
    validated_data,
    images
):

    amenities = validated_data.pop(
        "amenities",
        []
    )

    property_instance = Property.objects.create(
        owner=user,
        **validated_data
    )

    if images:

        for image in images:

            PropertyImage.objects.create(
                property=property_instance,
                image=image
            )


    if amenities:

        property_amenities = [

            PropertyAmenity(
                property=property_instance,
                amenity=amenity
            )

            for amenity in amenities
        ]

        PropertyAmenity.objects.bulk_create(
            property_amenities
        )

    return property_instance


# =========================================
# UPDATE PROPERTY
# =========================================
@transaction.atomic
def update_property_service(
    property_instance,
    validated_data,
    images=None,
    existing_image_ids=None
):

    amenities = validated_data.pop(
        "amenities",
        None
    )


    for key, value in validated_data.items():

        setattr(
            property_instance,
            key,
            value
        )

    property_instance.save()

    if amenities is not None:

        PropertyAmenity.objects.filter(
            property=property_instance
        ).delete()

        property_amenities = [

            PropertyAmenity(
                property=property_instance,
                amenity=amenity
            )

            for amenity in amenities
        ]

        PropertyAmenity.objects.bulk_create(
            property_amenities
        )


    if existing_image_ids is not None:

        # Delete removed images

        PropertyImage.objects.filter(
            property=property_instance
        ).exclude(
            id__in=existing_image_ids
        ).delete()


    if images:

        for image in images:

            PropertyImage.objects.create(
                property=property_instance,
                image=image
            )

    return property_instance


# =========================================
# DELETE PROPERTY
# =========================================

@transaction.atomic
def delete_property_service(
    property_instance
):

    property_instance.delete()

    return True


# =========================================
# GET OWNER PROPERTIES
# =========================================

def get_owner_properties_service(
    user
):

    return Property.objects.filter(
        owner=user
    ).prefetch_related(
        "images",
        "property_amenities__amenity"
    ).order_by("-created_at")


# =========================================
# GET SINGLE PROPERTY
# =========================================

def get_single_property_service(
    user,
    property_id
):

    return get_object_or_404(

        Property.objects.prefetch_related(
            "images",
            "property_amenities__amenity"
        ),

        id=property_id,
        owner=user
    )


# =========================================
# ADD PROPERTY IMAGES
# =========================================

@transaction.atomic
def upload_property_images_service(
    user,
    property_id,
    images
):

    # -------------------------
    # Get property
    # -------------------------

    property_instance = get_object_or_404(
        Property,
        id=property_id,
        owner=user
    )

    # -------------------------
    # Validate images
    # -------------------------

    if not images:

        raise Exception(
            "No images uploaded"
        )

    # -------------------------
    # Save images
    # -------------------------

    uploaded_images = []

    for image in images:

        obj = PropertyImage.objects.create(
            property=property_instance,
            image=image
        )

        uploaded_images.append(obj)

    return uploaded_images


# =========================================
# DELETE PROPERTY IMAGE
# =========================================

@transaction.atomic
def delete_property_image_service(
    user,
    image_id
):

    image = get_object_or_404(
        PropertyImage,
        id=image_id,
        property__owner=user
    )

    image.delete()

    return True