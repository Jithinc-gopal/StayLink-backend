from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer,BrokerProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import OwnerProfileSerializer,PartnerRegisterSerializer
from ..permissions import IsOwner, IsBroker 
from rest_framework import status
from rest_framework.decorators import api_view
from ..models import BrokerProfile
from accounts.services.auth_service import register_user
from accounts.services.auth_service import login_user
from accounts.services.auth_service import logout_user
from accounts.services.profile_service import create_owner_profile,get_owner_profile,update_owner_profile
from accounts.services.profile_service import create_broker_profile
from accounts.services.auth_service import google_auth
from accounts.services.password_service import send_forgot_password_email, reset_password




class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            data = register_user(serializer)
            return Response(data, status=201)

        return Response(serializer.errors, status=400)




class PartnerRegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PartnerRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            data = register_user(serializer)

            return Response(data, status=201)

        return Response(serializer.errors, status=400)



class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = login_user(
                request.data.get("email"),
                request.data.get("password")
            )
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=401)
        



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logout_user(request.data.get("refresh"))
            return Response({"message": "Logout successful"}, status=205)
        except:
            return Response({"error": "Invalid token"}, status=400)





class OwnerProfileCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request):
        serializer = OwnerProfileSerializer(data=request.data)

        if serializer.is_valid():
            try:
                profile = create_owner_profile(request.user, serializer)
                return Response({
                    "message": "Owner profile created successfully",
                    "data": OwnerProfileSerializer(profile).data
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)

   
    def get(self, request):
        try:
            profile = get_owner_profile(request.user)
            serializer = OwnerProfileSerializer(profile)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=404)

    
    def put(self, request):
        try:
            profile = get_owner_profile(request.user)

            serializer = OwnerProfileSerializer(
                profile,
                data=request.data,
                partial=True  # ✅ allows partial update
            )

            if serializer.is_valid():
                updated_profile = update_owner_profile(request.user, serializer)

                return Response({
                    "message": "Profile updated successfully",
                    "data": OwnerProfileSerializer(updated_profile).data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
    
    
    
  
  
class BrokerProfileCreateView(APIView):

    permission_classes = [IsAuthenticated, IsBroker]

    # =========================
    # CREATE PROFILE
    # =========================
    def post(self, request):

        serializer = BrokerProfileSerializer(
            data=request.data
        )

        if serializer.is_valid():

            try:

                profile = create_broker_profile(
                    request.user,
                    serializer
                )

                return Response({
                    "message": "Profile created successfully",
                    "data": BrokerProfileSerializer(profile).data
                }, status=201)

            except Exception as e:

                return Response({
                    "error": str(e)
                }, status=400)

        return Response(serializer.errors, status=400)

    # =========================
    # GET PROFILE
    # =========================
    def get(self, request):

        try:

            profile = BrokerProfile.objects.get(
                user=request.user
            )

            serializer = BrokerProfileSerializer(
                profile
            )

            return Response(
                serializer.data,
                status=200
            )

        except BrokerProfile.DoesNotExist:

            return Response({
                "error": "Broker profile not found"
            }, status=404)

    # =========================
    # UPDATE PROFILE
    # =========================
    def put(self, request):

        try:

            profile = BrokerProfile.objects.get(
                user=request.user
            )

            serializer = BrokerProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():

                serializer.save()

                return Response({
                    "message": "Profile updated successfully",
                    "data": serializer.data
                }, status=200)

            return Response(
                serializer.errors,
                status=400
            )

        except BrokerProfile.DoesNotExist:

            return Response({
                "error": "Broker profile not found"
            }, status=404)
    
    
    
class BrokerStatusView(APIView):

    permission_classes = [IsAuthenticated, IsBroker]

    def get(self, request):

        try:

            profile = BrokerProfile.objects.get(
                user=request.user
            )

            return Response({
                "profile_completed": True,
                "verification_status": profile.verification_status
            })

        except BrokerProfile.DoesNotExist:

            return Response({
                "profile_completed": False,
                "verification_status": "pending"
            })  
    


@api_view(['POST'])
def google_login(request):
    try:
        data = google_auth(request.data.get("token"))
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
    

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get("email")
            data = send_forgot_password_email(email)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)





class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            uid = request.data.get("uid")
            token = request.data.get("token")
            password = request.data.get("password")

            data = reset_password(uid, token, password)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)    