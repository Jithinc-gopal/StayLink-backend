from ..models import Property, PropertyImage

def create_property(user, validated_data, images):

    property_instance = Property.objects.create(
        owner=user,
        **validated_data
    )

    
    for img in images:
        PropertyImage.objects.create(property=property_instance, image=img)

    return property_instance


def get_owner_properties(user):
    return Property.objects.filter(owner=user)