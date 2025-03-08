import json
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate
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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
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

# @api_view(['GET'])
# @permission_classes([IsAdminUser])  # จำกัดให้เฉพาะ Admin ดูข้อมูลได้
# def user_list(request):
#     users = User.objects.all()
#     serializer = UserSerializer(users, many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def user_detail(request, id):
#     try:
#         user = User.objects.get(id=id)
#         profile = Usersdetail.objects.get(user=user)
#         user_data = UserSerializer(user).data
#         profile_data = UsersdetailSerializer(profile).data
#         return Response({**user_data, **profile_data})
#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=404)
#     except Usersdetail.DoesNotExist:
#         return Response({'error': 'Profile not found'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])  # ✅ อนุญาตให้ทุกคนเข้าถึง
def user_list(request):
    users = User.objects.all()
    user_data = []

    for user in users:
        user_serialized = UserSerializer(user).data
        try:
            profile = Usersdetail.objects.get(user=user)
            profile_serialized = UsersdetailSerializer(profile).data
        except Usersdetail.DoesNotExist:
            profile_serialized = {}  # ถ้าผู้ใช้ไม่มีโปรไฟล์ ให้ส่งข้อมูลว่าง

        user_data.append({**user_serialized, **profile_serialized})  # รวมข้อมูลทั้งสองส่วน

    return Response(user_data)

logger = logging.getLogger(__name__)
# ✅ View to get all hotels
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def view_all_hotels(request):
    """Retrieve all hotels"""
    try:
        hotels = Hotel.objects.all()
        serializer = HotelSerializer(hotels, many=True, context={"request": request})

        logger.info("✅ Successfully retrieved hotel data")  # ✅ Log success
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"❌ Error retrieving hotels: {str(e)}")  # ✅ Log error
        return Response({"detail": "Failed to retrieve hotels", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def view_hotel_details(request, hotel_id):
    """
    ✅ GET: Retrieve hotel details along with available rooms.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    hotel_serializer = HotelSerializer(hotel, context={"request": request})
    
    # ✅ Fetch all rooms for the given hotel
    rooms = Room.objects.filter(hotel=hotel)
    room_serializer = RoomSerializer(rooms, many=True, context={"request": request})

    return Response({
        "hotel": hotel_serializer.data,
        "rooms": room_serializer.data
    }, status=status.HTTP_200_OK)
    
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_hotel(request):
    try:
        data = request.data.copy()

        if 'imgHotel' in request.FILES:
            print(f"Received image: {request.FILES['imgHotel'].name} ({request.FILES['imgHotel'].size} bytes)")
        else:
            print("No image file received")

        serializer = HotelSerializer(data=request.data, context={'request': request})
        print("Data being sent to serializer:", data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)  # แสดง errors เพื่อการ debug
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("Exception:", str(e))  # แสดงข้อความ exception ที่เกิดขึ้น
        return Response({"detail": "Failed to add hotel", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_hotel(request, hotel_id):
    
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)  # Ensure user owns the hotel
    hotel.delete()
    return Response({"detail": "Hotel deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



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
        pets = Pet.objects.filter(owner=request.user)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pet_list_create(request):
    try:
        serializer = PetSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"detail": "Failed to add pet", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pet_list_delete(request, pet_id):
    try:
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)  # Ensure pet belongs to user
        pet.delete()
        return Response({"detail": "Pet deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"detail": "Failed to delete pet", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_hotel_rooms(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_hotel_details(request, hotel_id):
    """
    ✅ Retrieve hotel details along with associated rooms.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)
    hotel_serializer = HotelSerializer(hotel, context={"request": request})

    # ✅ Fetch rooms associated with this hotel
    rooms = Room.objects.filter(hotel=hotel)
    room_serializer = RoomSerializer(rooms, many=True, context={"request": request})

    return Response({
        "hotel": hotel_serializer.data,
        "rooms": room_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def update_hotel_details(request, hotel_id):
    """
    ✅ Update hotel details, including optional image upload and rooms.
    """
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # ✅ Handle image upload separately
    data = request.data.copy()
    if "imgHotel" in request.FILES:
        data["imgHotel"] = request.FILES["imgHotel"]

    # ✅ Ensure 'rooms' is properly parsed
    if "rooms" in data:
        try:
            data["rooms"] = json.loads(data["rooms"])
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format for rooms"}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Ensure 'facilities' is properly parsed
    if "facilities" in data:
        try:
            data["facilities"] = json.loads(data["facilities"])
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format for facilities"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = HotelSerializer(hotel, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def hotel_rooms(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)
    
    rooms = Room.objects.filter(hotel=hotel)
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def hotel_facilities(request, hotel_id):
    try:
        facilities = FacilitiesHotel.objects.get(hotel_id=hotel_id)
    except FacilitiesHotel.DoesNotExist:
        return Response({'error': 'Facilities not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = FacilitiesHotelSerializer(facilities)
    return Response(serializer.data)