from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import (MultiPartParser,FormParser)
from ..permissions import (IsOwner,IsVerifiedOwner)
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

    permission_classes = [IsAuthenticated,IsVerifiedOwner,IsOwner]
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
            status=status.HTTP_200_OK
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
                status=status.HTTP_200_OK
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