from rest_framework import serializers
from ..models import CustomUser
from ..models import OwnerProfile,BrokerProfile
import re



class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:

        model = CustomUser

        fields = [
            "first_name",
            "email",
            "password",
            "confirm_password"
        ]

        extra_kwargs = {

            "password": {
                "write_only": True
            },

            # IMPORTANT FIX
            "email": {
                "validators": []
            }
        }

    def validate(self, data):

        if (
            data["password"] !=
            data["confirm_password"]
        ):

            raise serializers.ValidationError(
                "Passwords do not match"
            )

        return data

    def create(self, validated_data):

        validated_data.pop(
            "confirm_password"
        )

        user = CustomUser.objects.create_user(
            **validated_data
        )

        return user
        


class PartnerRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser

        fields = [
            'first_name',
            'email',
            'role',
            'password',
            'confirm_password',
        ]

    def validate(self, data):

        if data['role'] not in ['owner', 'broker']:

            raise serializers.ValidationError(
                "Invalid role"
            )

        if data['password'] != data['confirm_password']:

            raise serializers.ValidationError(
                "Passwords do not match"
            )

        if CustomUser.objects.filter(email=data['email']).exists():

            raise serializers.ValidationError(
                "Email already registered"
            )

        return data

    def create(self, validated_data):

        validated_data.pop('confirm_password')

        user = CustomUser.objects.create_user(
            first_name=validated_data['first_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
            is_active=False
        )

        return user



class OwnerProfileSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    read_only_fields = ['user', 'verification_status']

    class Meta:
        model = OwnerProfile
        fields = '__all__'
        read_only_fields = ['user']

    def validate_phone(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError(
                "Enter a valid 10-digit phone number"
            )
        return value

    def validate_pincode(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError(
                "Enter a valid 6-digit pincode"
            )
        return value

    def validate(self, data):

        required_fields = [
            'address',
            'city',
            'district',
            'state',
            'pincode'
        ]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: "This field is required"}
                )

        return data

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "email": obj.user.email,
        }
        
        

class BrokerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerProfile
        fields = '__all__'
        read_only_fields = ['user', 'verification_status']

   
    def validate_phone(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Enter a valid 10-digit phone number")
        return value

    
    def validate_pincode(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("Enter a valid 6-digit pincode")
        return value

    
    def validate_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience cannot be negative")
        if value > 50:
            raise serializers.ValidationError("Experience seems unrealistic")
        return value


    def validate(self, data):
        required_fields = [
            'phone',
            'address',
            'city',
            'district',
            'state',
            'pincode',
            'agency_name',
            'experience'
        ]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required"})

        return data      
        
        
        
      