from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (MultiPartParser,FormParser)
from ..permissions import (IsVerifiedOwner)
from accounts.permissions import IsOwner
from ..models import (Amenity,Property)
from owner.serializers.property_serializers import (AmenitySerializer,PropertySerializer,PropertyImageSerializer)
from owner.services.property_service import (
    create_property_service,
    update_property_service,
    delete_property_service,
    get_owner_properties_service,
    get_single_property_service,
    upload_property_images_service,
    delete_property_image_service
)

class PropertyView(APIView):

   
    permission_classes = [IsAuthenticated, IsOwner, IsVerifiedOwner]
    parser_classes = [MultiPartParser,FormParser]


    def post(self, request):

        serializer = PropertySerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():

            images = request.FILES.getlist(
                "images"
            )

            property_instance = (
                create_property_service(
                    user=request.user,
                    validated_data=serializer.validated_data,
                    images=images
                )
            )

            return Response(
                PropertySerializer(
                    property_instance,
                    context={"request": request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def put(self, request, pk):

        property_instance = (
            get_single_property_service(
                request.user,
                pk
            )
        )

        serializer = PropertySerializer(
            property_instance,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():

            images = request.FILES.getlist(
                "images"
            )

            existing_image_ids = request.data.getlist(
                "existing_images"
            )

            if existing_image_ids:

                existing_image_ids = [
                    int(id)
                    for id in existing_image_ids
                ]

            else:

                existing_image_ids = None

            updated_property = (
                update_property_service(
                    property_instance=property_instance,
                    validated_data=serializer.validated_data,
                    images=images,
                    existing_image_ids=existing_image_ids
                )
            )

            return Response(
                PropertySerializer(
                    updated_property,
                    context={"request": request}
                ).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request, pk):

        property_instance = (
            get_single_property_service(
                request.user,
                pk
            )
        )

        delete_property_service(
            property_instance
        )

        return Response(
            {
                "message":
                "Property deleted successfully"
            },
            status=status.HTTP_204_NO_CONTENT
        )


    def get(self, request, pk=None):

        if pk:

            property_instance = (
                get_single_property_service(
                    request.user,
                    pk
                )
            )

            serializer = PropertySerializer(
                property_instance,
                context={"request": request}
            )

            return Response(serializer.data)


        properties = (
            get_owner_properties_service(
                request.user
            )
        )

        serializer = PropertySerializer(
            properties,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)




class OwnerPropertyListView(APIView):

    permission_classes = [IsAuthenticated,IsOwner]

    def get(self, request):

        properties = (
            get_owner_properties_service(
                request.user
            )
        )

        serializer = PropertySerializer(
            properties,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)




class PropertyImageView(APIView):

    permission_classes = [
            IsAuthenticated,
            IsOwner,
            IsVerifiedOwner
        ]


    def post(self, request, property_id):

        try:

            images = request.FILES.getlist(
                "images"
            )

            uploaded_images = (
                upload_property_images_service(
                    user=request.user,
                    property_id=property_id,
                    images=images
                )
            )


            serializer = (
                PropertyImageSerializer(
                    uploaded_images,
                    many=True,
                    context={"request": request}
                )
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


    def delete(self, request, image_id):

        try:

            delete_property_image_service(
                user=request.user,
                image_id=image_id
            )

            return Response(
                {
                    "message":
                    "Image deleted successfully"
                },
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )





class AmenityListView(APIView):

    permission_classes = [
    IsAuthenticated,
    IsOwner
    ]  

    def get(self, request):

        amenities = Amenity.objects.all()

        serializer = AmenitySerializer(
            amenities,
            many=True
        )

        return Response(serializer.data)
    
    
    
    
class PublicPropertyListView(APIView):
    """
    Public endpoint — no authentication needed.
    The FastAPI AI service calls this to get all active properties.
    Includes property details, amenities, and average rating.
    """
    permission_classes = []  # no auth — AI service needs open access

    def get(self, request):
        from traveler.models import Review
        from django.db.models import Avg

        properties = Property.objects.filter(
            status="active",
            is_available=True
        ).prefetch_related(
            "images",
            "property_amenities__amenity",
            "reviews"
        )

        data = []
        for p in properties:

            # Get all amenity names for this property
            amenities = [
                pa.amenity.name
                for pa in p.property_amenities.all()
            ]

            # Get average rating from reviews
            avg_rating = p.reviews.aggregate(
                avg=Avg("rating")
            )["avg"]

            data.append({
                "id": p.pk,
                "title": p.title,
                "description": p.description,
                "property_type": p.property_type,
                "price": str(p.price),
                "price_unit": p.price_unit,
                "city": p.city,
                "state": p.state,
                "address": p.address,
                "bedrooms": p.bedrooms,
                "bathrooms": p.bathrooms,
                "max_guest": p.max_guest,
                "is_furnished": p.is_furnished,
                "ambience": p.ambience or "",
                "nearby_facilities": p.nearby_facilities,
                "rules": p.rules,
                "cancellation_policy": p.cancellation_policy,
                "amenities": amenities,
                "avg_rating": round(avg_rating, 1) if avg_rating else None,
                "latitude": str(p.latitude) if p.latitude else None,
                "longitude": str(p.longitude) if p.longitude else None,
            })

        return Response(data)    