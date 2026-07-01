from rest_framework import serializers
from accounts.models import OwnerProfile, BrokerProfile
from django.contrib.auth import get_user_model
from owner.models import Property, PropertyImage
from bookings.models import Booking
from payments.models import Payment


User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    """Basic user info embedded inside profile serializers"""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'date_joined',
        ]


class AdminOwnerProfileSerializer(serializers.ModelSerializer):
    user = AdminUserSerializer(read_only=True)

    class Meta:
        model = OwnerProfile
        fields = [
            'id',
            'user',
            'phone',
            'address',
            'city',
            'district',
            'state',
            'pincode',
            'profile_image',
            'id_proof',
            'verification_status',
            'rejection_reason',
        ]


class AdminBrokerProfileSerializer(serializers.ModelSerializer):
    user = AdminUserSerializer(read_only=True)

    class Meta:
        model = BrokerProfile
        fields = [
            'id',
            'user',
            'phone',
            'address',
            'city',
            'district',
            'state',
            'pincode',
            'agency_name',
            'experience',
            'license_number',
            'profile_image',
            'id_proof',
            'verification_status',
            'rejection_reason',
        ]
        
    

class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Full detail of a single user for admin view.
    Shows profile info depending on their role.
    """
    owner_profile = serializers.SerializerMethodField()
    broker_profile = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'is_staff',
            'profile_completed',
            'date_joined',
            'last_login',
            'owner_profile',
            'broker_profile',
            'total_bookings',
        ]

    def get_owner_profile(self, obj):
        if obj.role == 'owner':
            try:
                profile = obj.ownerprofile
                return {
                    'verification_status': profile.verification_status,
                    'city': profile.city,
                    'phone': profile.phone,
                    'profile_image': self.context['request'].build_absolute_uri(
                        profile.profile_image.url
                    ) if profile.profile_image else None,
                }
            except Exception:
                return None
        return None

    def get_broker_profile(self, obj):
        if obj.role == 'broker':
            try:
                profile = obj.brokerprofile
                return {
                    'verification_status': profile.verification_status,
                    'agency_name': profile.agency_name,
                    'city': profile.city,
                    'phone': profile.phone,
                    'profile_image': self.context['request'].build_absolute_uri(
                        profile.profile_image.url
                    ) if profile.profile_image else None,
                }
            except Exception:
                return None
        return None

    def get_total_bookings(self, obj):
        if obj.role == 'user':
            return obj.traveler_bookings.count()
        return None


class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Compact user info for the list view.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'profile_completed',
            'date_joined',
        ]        
        
        
    

class AdminPropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image']


class AdminPropertyListSerializer(serializers.ModelSerializer):
    """
    Compact property info for the list view.
    """
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    images = AdminPropertyImageSerializer(many=True, read_only=True)
    total_bookings = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'property_type',
            'city',
            'state',
            'price',
            'price_unit',
            'status',
            'is_available',
            'owner_email',
            'owner_name',
            'images',
            'total_bookings',
            'created_at',
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()

    def get_total_bookings(self, obj):
        return obj.bookings.count()


class AdminBookingSerializer(serializers.ModelSerializer):
    """
    Compact booking info shown inside property detail.
    """
    traveler_email = serializers.CharField(
        source='traveler.email',
        read_only=True
    )
    traveler_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'traveler_email',
            'traveler_name',
            'check_in',
            'check_out',
            'guests_count',
            'total_amount',
            'advance_amount',
            'status',
            'payment_status',
            'created_at',
        ]

    def get_traveler_name(self, obj):
        return f"{obj.traveler.first_name} {obj.traveler.last_name}".strip()


class AdminPropertyDetailSerializer(serializers.ModelSerializer):
    """
    Full property detail including images and bookings.
    """
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    images = AdminPropertyImageSerializer(many=True, read_only=True)
    bookings = serializers.SerializerMethodField()
    total_bookings = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'property_type',
            'price',
            'price_unit',
            'address',
            'city',
            'state',
            'bedrooms',
            'bathrooms',
            'max_guest',
            'is_furnished',
            'is_available',
            'status',
            'admin_note',
            'owner_email',
            'owner_name',
            'images',
            'bookings',
            'total_bookings',
            'total_revenue',
            'created_at',
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()

    def get_bookings(self, obj):
        bookings = obj.bookings.order_by('-created_at')
        return AdminBookingSerializer(bookings, many=True).data

    def get_total_bookings(self, obj):
        return obj.bookings.count()

    def get_total_revenue(self, obj):
        from django.db.models import Sum
        total = obj.bookings.filter(
            status__in=['confirmed', 'completed']
        ).aggregate(total=Sum('total_amount'))['total']
        return float(total) if total else 0.0   
    
    


class AdminPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'razorpay_order_id',
            'razorpay_payment_id',
            'amount',
            'status',
            'created_at',
        ]


class AdminBookingDetailSerializer(serializers.ModelSerializer):
    """
    Full booking detail for admin view.
    Includes property, traveler, and payment info.
    """
    traveler_email = serializers.CharField(
        source='traveler.email',
        read_only=True
    )
    traveler_name = serializers.SerializerMethodField()
    traveler_phone = serializers.SerializerMethodField()

    property_title = serializers.CharField(
        source='property.title',
        read_only=True
    )
    property_city = serializers.CharField(
        source='property.city',
        read_only=True
    )
    owner_email = serializers.CharField(
        source='property.owner.email',
        read_only=True
    )
    owner_name = serializers.SerializerMethodField()

    payment = AdminPaymentSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'traveler_email',
            'traveler_name',
            'traveler_phone',
            'property_title',
            'property_city',
            'owner_email',
            'owner_name',
            'check_in',
            'check_out',
            'check_in_time',
            'check_out_time',
            'guests_count',
            'special_request',
            'total_amount',
            'advance_amount',
            'status',
            'payment_status',
            'payment',
            'created_at',
            'updated_at',
        ]

    def get_traveler_name(self, obj):
        return f"{obj.traveler.first_name} {obj.traveler.last_name}".strip()

    def get_traveler_phone(self, obj):
        # traveler role is 'user' in your system
        # phone is not on CustomUser directly so return None if not found
        try:
            return obj.traveler.ownerprofile.phone
        except Exception:
            return None

    def get_owner_name(self, obj):
        return f"{obj.property.owner.first_name} {obj.property.owner.last_name}".strip()


class AdminBookingListSerializer(serializers.ModelSerializer):
    """
    Compact booking info for the list view.
    """
    traveler_email = serializers.CharField(
        source='traveler.email',
        read_only=True
    )
    traveler_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(
        source='property.title',
        read_only=True
    )
    property_city = serializers.CharField(
        source='property.city',
        read_only=True
    )
    owner_email = serializers.CharField(
        source='property.owner.email',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'traveler_email',
            'traveler_name',
            'property_title',
            'property_city',
            'owner_email',
            'check_in',
            'check_out',
            'guests_count',
            'total_amount',
            'advance_amount',
            'status',
            'payment_status',
            'created_at',
        ]

    def get_traveler_name(self, obj):
        return f"{obj.traveler.first_name} {obj.traveler.last_name}".strip()