from rest_framework import serializers
from .models import Property, PropertyImage




class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image"]
        


class PropertySerializer(serializers.ModelSerializer):

    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = "__all__"
        read_only_fields = ["owner", "status"]

    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_privacy_level(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Privacy level must be between 1 and 5")
        return value        