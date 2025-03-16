# Python Standard Library
import json
import logging
from datetime import datetime

# Django imports
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.timezone import make_aware

# Django REST Framework
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from .models import Hotel, HotelApproval, Reservation
from .serializers import *

@api_view(['GET'])
@authentication_classes([TokenAuthentication])  
@permission_classes([IsAuthenticated])  
def get_current_user(request):
    user = request.user
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff  # ✅ เพิ่ม is_staff
    })

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
    print(serializer.errors)
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


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reservation_list(request):
    print(f"🔍 Token in request: {request.auth}")
    print(f"👤 User: {request.user}")
    print(f"👤 is_authenticated: {request.user.is_authenticated}")
    print(f"👤 is_staff (Admin): {request.user.is_staff}")

    if request.user.is_staff:
        # ✅ Admin เห็นทุก Reservation
        reservations = Reservation.objects.all()
    else:
        # ✅ ผู้ใช้ทั่วไป เห็นเฉพาะของตัวเอง
        reservations = Reservation.objects.filter(pet_owner=request.user)

    print(f"📌 Reservation Data: {reservations.values('id', 'pet_owner_id', 'pet_id', 'room_id')}")
    
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reservation_detail(request, id):  # ✅ ต้องใช้ "id" ให้ตรงกับ URL
    try:
        reservation = Reservation.objects.get(id=id)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow all users to access
def user_list(request):
    users = User.objects.all()  # Get all users
    user_data = []

    for user in users:
        user_serialized = UserSerializer(user).data
        
        # Try to get the user profile (Usersdetail)
        try:
            profile = Usersdetail.objects.get(user=user)
            profile_serialized = UsersdetailSerializer(profile).data
            user_status = profile.status  # Get the status from the Usersdetail model
        except Usersdetail.DoesNotExist:
            profile_serialized = {}  # If the user doesn't have a profile, send empty data
            user_status = "N/A"  # Default value for status if no profile exists

        # Combine both user data and profile data, including status
        user_data.append({
            **user_serialized,
            **profile_serialized,
            "status": user_status  # Add the status to the result
        })

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


# อัพเดตสเตตัสสำหรับ admin page
@api_view(['GET', 'PUT', 'PATCH'])  # Allow GET, PUT, PATCH methods
@permission_classes([AllowAny])  # Allow access to anyone
def update_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)  # Get the user by ID
        userdetail = user.usersdetail  # Access the related Usersdetail instance using user.usersdetail
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Usersdetail.DoesNotExist:
        return Response({'detail': 'User detail not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Return the user's current status
        return Response({'status': userdetail.status}, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        # For PUT and PATCH, get the new status value
        status_value = request.data.get('status')
        if not status_value:
            return Response({'detail': 'Status field is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure the status is valid (should be from the choices in the model)
        if status_value not in [choice[0] for choice in Usersdetail.Status.choices]:
            return Response({'detail': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the status of the Usersdetail
        userdetail.status = status_value
        userdetail.save()

        return Response({'status': userdetail.status}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def hotel_list(request):
    hotels = Hotel.objects.all()
    hotel_data = []

    for hotel in hotels:
        try:
            approval = HotelApproval.objects.get(hotel=hotel)
            approval_status = approval.status  
            approved_by = approval.approved_by.username if approval.approved_by else None
            approved_at = approval.reviewed_at
            reason = approval.reason  # ✅ เพิ่ม reason ที่ได้จาก HotelApproval
        except HotelApproval.DoesNotExist:
            approval_status = "pending"
            approved_by = None
            approved_at = None
            reason = None  # ✅ ถ้าไม่มีให้ใส่เป็น None

        hotel_data.append({
            "id": hotel.id,
            "name": hotel.name,
            "registrant": hotel.owner.username,
            "status": approval_status,
            "approved_by": approved_by,
            "approved_at": approved_at,
            "reason": reason  # ✅ ใส่ reason ลงไป
        })

    return Response(hotel_data, status=status.HTTP_200_OK)



# @api_view(['PATCH'])
# @permission_classes([IsAuthenticated])  # Ensure only authenticated users can update the status
# def update_hotel_status(request, hotel_id):
#     try:
#         hotel = Hotel.objects.get(id=hotel_id)
#     except Hotel.DoesNotExist:
#         return Response({'detail': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

#     status_value = request.data.get('status')
#     if status_value not in ['pending', 'confirmed', 'cancelled']:
#         return Response({'detail': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

#     hotel.is_verified = status_value == 'confirmed'
#     hotel.save()

#     return Response({'status': hotel.is_verified}, status=status.HTTP_200_OK)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_hotel_status(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'detail': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get('status')

    if status_value not in ['pending', 'confirmed', 'cancelled']:
        return Response({'detail': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ อัปเดต status ของ Hotel
    hotel.status = status_value  
    hotel.is_verified = (status_value == 'confirmed')  # ✅ confirmed -> True, อื่นๆ -> False
    hotel.save()

    # ✅ ตรวจสอบว่า HotelApproval มีอยู่หรือไม่
    hotel_approval, created = HotelApproval.objects.get_or_create(hotel=hotel)

    # ✅ ถ้ามีอยู่แล้วให้แก้ไข status
    hotel_approval.status = status_value
    hotel_approval.approved_by = request.user  # อัปเดตคนอนุมัติ (ใส่ None ถ้าไม่ระบุ)
    hotel_approval.save()

    return Response({
        'hotel_status': hotel.status,
        'approval_status': hotel_approval.status
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])  # ใช้ IsAuthenticated หากต้องการให้ผู้ใช้ล็อกอินเข้าถึง
def hotel_approval_status(request, hotel_id):
    try:
        # ค้นหาการอนุมัติโรงแรมจาก ID
        approval = HotelApproval.objects.get(hotel_id=hotel_id)
    except HotelApproval.DoesNotExist:
        return Response({'detail': 'Hotel approval not found'}, status=status.HTTP_404_NOT_FOUND)

    # ส่งกลับสถานะการอนุมัติของโรงแรม
    return Response({
        'hotel': approval.hotel.name,
        'status': approval.get_status_display(),
        'approved_by': approval.approved_by.username if approval.approved_by else None,
        'reason': approval.reason,
        'reviewed_at': approval.reviewed_at
    }, status=status.HTTP_200_OK)
    
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


@api_view(['PATCH'])  # ✅ ต้องมี @api_view
@permission_classes([IsAuthenticated])
def update_hotel_reason(request, hotel_id):
    print("🚀 update_hotel_reason ถูกเรียกใช้")  # Debug

    try:
        hotel_approval = HotelApproval.objects.get(hotel_id=hotel_id)
    except HotelApproval.DoesNotExist:
        return Response({'detail': 'Hotel approval not found'}, status=status.HTTP_404_NOT_FOUND)

    reason_value = request.data.get('reason')
    if not reason_value:
        return Response({'detail': 'Reason field is required'}, status=status.HTTP_400_BAD_REQUEST)

    hotel_approval.reason = reason_value
    hotel_approval.save()

    return Response({'status': 'Reason updated successfully', 'reason': hotel_approval.reason}, status=status.HTTP_200_OK)

# ✅ API ดึงข้อมูลการจองทั้งหมด
@api_view(['GET'])
def get_all_reservations(request):
    reservations = Reservation.objects.all()
    serializer = ReservationSerializer(reservations, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_reservation_status(request, reservation_id):
    try:
        print(f"🔍 Request received to update reservation ID: {reservation_id}")
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ ตรวจสอบสิทธิ์เฉพาะ admin หรือเจ้าของ
    if not request.user.is_staff and request.user != reservation.pet_owner:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get("status")
    print(f"🔄 Updating status to: {new_status}")

    if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    reservation.status = new_status
    reservation.save()
    print("✅ Status updated successfully!")

    return Response({"success": "Status updated", "status": new_status})


    

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
    # เพิ่ม print statements เพื่อตรวจสอบข้อมูลที่ได้รับ
    print(f"Updating hotel with ID: {hotel_id}")
    print(f"Request data: {request.data}")
    print(f"Request FILES: {request.FILES}")
    
    try:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        print(f"Found hotel: {hotel.name} (ID: {hotel.id})")

        # ✅ Handle image upload separately
        data = request.data.copy()
        # ถ้า imgHotel เป็น URL และไม่มีไฟล์ใหม่ส่งมา ให้ลบออกเพื่อไม่ให้ serializer ตรวจสอบ
        if "imgHotel" in data and not request.FILES.get("imgHotel"):
            # ตรวจสอบว่าเป็น URL หรือไม่
            if isinstance(data["imgHotel"], str) and (data["imgHotel"].startswith('http://') or data["imgHotel"].startswith('https://')):
                del data["imgHotel"]  # ลบออกเพื่อไม่ให้ serializer พยายามตรวจสอบ
        
        # ถ้ามีไฟล์ใหม่ ให้ใช้ไฟล์จาก request.FILES
        if "imgHotel" in request.FILES:
            data["imgHotel"] = request.FILES["imgHotel"]
        
        print(f"Data being sent to serializer: {data}")
        
        serializer = HotelSerializer(hotel, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print("Hotel updated successfully!")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # พิมพ์รายละเอียดข้อผิดพลาดจาก serializer
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # จับข้อผิดพลาดทั้งหมดที่อาจเกิดขึ้น
        print(f"Exception occurred: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def hotel_rooms(request, hotel_id):
    """Retrieve all rooms for a specific hotel"""
    try:
        rooms = Room.objects.filter(hotel_id=hotel_id)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Room.DoesNotExist:
        return Response({"error": "Rooms not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_room_details(request, room_id=None):
    """
    ✅ GET: Retrieve room details. If room_id exists, it's edit mode; otherwise, it's create mode.
    """
    if room_id:
        room = get_object_or_404(Room, id=room_id)
        serializer = RoomSerializer(room)
        return Response({"mode": "edit", "room": serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({"mode": "create", "room": None}, status=status.HTTP_200_OK)
    
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_room(request, hotel_id):
    """✅ GET: Retrieve rooms | ✅ POST: Create a room for a hotel"""
    try:
        hotel = Hotel.objects.get(id=hotel_id)
        if not request.user.is_staff:
            return Response({"error": "Permission denied. Only staff members can create rooms."}, status=status.HTTP_403_FORBIDDEN)
        if request.method == "GET":
            rooms = Room.objects.filter(hotel=hotel)
            serializer = RoomSerializer(rooms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "POST":
            print("ข้อมูลที่ได้รับจาก request:", request.data)
            
            room_serializer = RoomSerializer(data=request.data)
            
            if room_serializer.is_valid():
                room = room_serializer.save(hotel=hotel)  # ✅ Assign hotel automatically
                
                # ✅ Save room facilities (if provided)
                facilities_data = request.data.get("facilities", None)
                if facilities_data:
                    facilities_serializer = FacilitiesRoomSerializer(data=facilities_data)
                    if facilities_serializer.is_valid():
                        facilities_serializer.save(room=room)

                return Response(room_serializer.data, status=status.HTTP_201_CREATED)
            print(room_serializer.errors)
            return Response(room_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print(Hotel.DoesNotExist)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def update_room(request, hotel_id):
    """✅ Update a specific room and its facilities under a hotel"""
    try:
        # ✅ Get `room_id` from request data
        room_id = request.data.get("room_id")
        print(f"🔍 Searching for room with id={room_id}, hotel_id={hotel_id}")

        # ✅ Use `filter().first()` to avoid `MultipleObjectsReturned`
        room = Room.objects.filter(id=room_id, hotel_id=hotel_id).first()

        if not room:
            print(f"❌ Room with id={room_id} in hotel_id={hotel_id} not found")
            return Response({"error": "Room not found"}, status=404)

        print(f"✅ Room found: {room}")

        # ✅ Serialize and validate room update data
        room_serializer = RoomSerializer(room, data=request.data, partial=True)

        if room_serializer.is_valid():
            print(f"✅ Room data validation successful")
            room_serializer.save()

            # ✅ Handle room facilities update if provided
            facilities_data = request.data.get("facilities")
            if facilities_data:
                print(f"🔍 Updating facilities for Room ID {room.id}")
                try:
                    # ✅ Try to retrieve existing facilities for the room
                    facilities_instance = FacilitiesRoom.objects.get(room=room)
                    facilities_serializer = FacilitiesRoomSerializer(
                        facilities_instance, data=facilities_data, partial=True
                    )
                except FacilitiesRoom.DoesNotExist:
                    print(f"❌ No existing facilities found for Room ID {room.id}, creating new ones.")

                    # ✅ Explicitly pass `room` when creating new facilities
                    facilities_data["room"] = room.id  # Associate room ID explicitly
                    facilities_serializer = FacilitiesRoomSerializer(data=facilities_data)

                if facilities_serializer.is_valid():
                    facilities_serializer.save()
                    print(f"✅ Facilities updated: {facilities_serializer.data}")
                else:
                    print(f"❌ Facilities validation errors: {facilities_serializer.errors}")
                    return Response(facilities_serializer.errors, status=400)

            print(f"✅ Updated Room Data: {room_serializer.data}")
            return Response(room_serializer.data, status=200)

        print(f"❌ Room validation errors: {room_serializer.errors}")
        return Response(room_serializer.errors, status=400)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return Response({"error": str(e)}, status=500)


    
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_hotel_facilities(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)

        # ✅ Auto-create facilities if they don’t exist
        facilities, created = FacilitiesHotel.objects.get_or_create(hotel=hotel)

        serializer = FacilitiesHotelSerializer(facilities)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def update_hotel_facilities(request, hotel_id):
    """✅ PUT: Update hotel facilities"""

    try:
        # Ensure the hotel exists
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get or create facilities for the hotel (handles missing records)
    facilities, created = FacilitiesHotel.objects.get_or_create(hotel=hotel)

    serializer = FacilitiesHotelSerializer(facilities, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Log validation errors
    print("❌ Validation Errors:", serializer.errors)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(["GET",])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def hotel_facilities(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)

        try:
            facilities = FacilitiesHotel.objects.get(hotel=hotel)
        except FacilitiesHotel.DoesNotExist:
            return Response({"error": "Facilities not found for this hotel"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacilitiesHotelSerializer(facilities)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ✅ บังคับให้ต้องมี Token
def create_reservation(request):
    print("🔍 Received Authorization Header:", request.headers.get("Authorization"))  # ✅ Debug
    print("🔍 User making request:", request.user)  # ✅ Debug
    if request.method == "POST":
        try:
            print("📩 Request Body:", request.body)  # ✅ Debugging
            data = json.loads(request.body)
            
            # ดึงค่าจาก request
            user = User.objects.get(id=data["user_id"])  # ดึงข้อมูลเจ้าของสัตว์เลี้ยง
            pet = Pet.objects.get(id=data["pet_id"])
            room = Room.objects.get(id=data["room_id"])
            
            check_in_date = make_aware(datetime.strptime(data["check_in"], "%Y-%m-%d"))
            check_out_date = make_aware(datetime.strptime(data["check_out"], "%Y-%m-%d"))
            total_price = room.price_per_night * ((check_out_date - check_in_date).days)

            # สร้างการจอง
            reservation = Reservation.objects.create(
                pet_owner=user,
                pet=pet,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                totalprice=total_price,
                status="pending",
                payment_status="unpaid",
                special_request=data.get("special_request", ""),
                cancellation_reason=""
            )

            return JsonResponse({"message": "Reservation created successfully!", "reservation_id": reservation.id}, status=201)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)

@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def check_room_availability(request):
    hotel_id = request.GET.get("hotel")
    room_id = request.GET.get("room")
    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")

    if not all([hotel_id, room_id, check_in, check_out]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    # ค้นหาการจองที่มีช่วงวันที่ทับซ้อนกัน
    overlapping_reservations = Reservation.objects.filter(
        room_id=room_id,
        check_in_date__lt=check_out,   # เช็คว่ามีการจองที่เริ่มต้นก่อนวัน Check-out
        check_out_date__gt=check_in,   # เช็คว่ามีการจองที่สิ้นสุดหลังวัน Check-in
        status__in=["pending", "confirmed"]  # ตรวจสอบเฉพาะการจองที่ยังใช้งานได้
    ).count()

    # ดึงข้อมูลห้องมาดูว่ามันเต็มไหม
    room = Room.objects.get(id=room_id)
    is_full = overlapping_reservations >= room.max_pets

    return JsonResponse({"available": not is_full})

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """Retrieve the authenticated user's info"""
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_hotel_staff": user.is_hotel_staff if hasattr(user, "is_hotel_staff") else False,
    })