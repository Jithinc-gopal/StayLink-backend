from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PropertySerializer
from .services.property_service import create_property
from .permissions import IsOwner
from .services.property_service import get_owner_properties



class AddPropertyView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):

        serializer = PropertySerializer(data=request.data)

        if serializer.is_valid():
            images = request.FILES.getlist("images")

            property_instance = create_property(
                user=request.user,
                validated_data=serializer.validated_data,
                images=images
            )

            return Response(
                PropertySerializer(property_instance).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    


class OwnerPropertyListView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        properties = get_owner_properties(request.user)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)
    
    
    
        