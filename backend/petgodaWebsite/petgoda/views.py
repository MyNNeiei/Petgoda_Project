from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'message': 'Registration successful.'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    print(serializer)
    print("🚨 Validation Errors:", serializer.errors)
    return Response({
        'errors': serializer.errors,
        'message': 'Invalid registration data'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_staff': user.is_staff,
            'message': 'Login successful.'
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK) 
    except Exception as e:
        return Response({
            'message': 'Error during logout',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_view(request):
    if request.method == 'GET':
        try:
            profile, created = Usersdetail.objects.get_or_create(user=request.user)
            print("🔍 User:", request.user.username)
            print("📸 Profile picture:", profile.picture if profile.picture else "No picture")

            serializer = UserProfileSerializer(request.user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": "Failed to fetch profile data", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def edit_profile_view(request):
    if request.method == 'PUT':
        try:
            profile, created = Usersdetail.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)

            if serializer.is_valid():
                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    if profile.picture:
                        profile.picture.delete()  # Delete old picture
                    profile.picture = request.FILES['profile_picture']
                    profile.save()

                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            print("❌ Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("❌ Server Error:", str(e))
            return Response(
                {"detail": "Failed to update profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reservation_list(request):
    if request.method == "GET":
        reservations = Reservation.objects.filter(pet_owner=request.user)
        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pet_owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_reservation_status(request, reservation_id):
    
    try:
        reservation = Reservation.objects.get(id=reservation_id, pet_owner=request.user)

        if reservation.status != "pending":
            return Response({"detail": "Only pending reservations can be modified."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReservationSerializer(reservation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Reservation.DoesNotExist:
        return Response({"detail": "Reservation not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pet_list_views(request):
    """
    ✅ GET: Retrieve all pets belonging to the logged-in user
    ✅ POST: Add a new pet for the logged-in user
    """
    if request.method == "GET":
        # ✅ Retrieve pets owned by the logged-in user
        pets = Pet.objects.filter(owner=request.user.usersdetail)  # Assuming `Usersdetail` has OneToOne with User
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pet_list_create(request):
    """
    ✅ GET: Retrieve all pets belonging to the logged-in user
    ✅ POST: Add a new pet for the logged-in user
    """
    if request.method == "POST":
        try:
            # ✅ Assign the pet to the logged-in user
            request.data["owner"] = request.user.usersdetail.id
            serializer = PetSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"detail": "Failed to add pet", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

