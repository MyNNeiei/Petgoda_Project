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
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import HotelApproval, Hotel
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework import generics, permissions
from petgoda.models import Reservation
from petgoda.models import Reservation
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from petgoda.models import Reservation
# from petgoda.api.serializers import ReservationSerializer # type: ignore


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

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Reservation
from .serializers import ReservationSerializer

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


# views.py


# @api_view(['PUT'])
# @permission_classes([AllowAny])  # ให้เฉพาะผู้ที่ล็อกอินเท่านั้นที่สามารถอัปเดตสถานะ
# def update_user_status(request, user_id):
#     print("5555")
#     try:
#         user = User.objects.get(id=user_id)  # ค้นหาผู้ใช้จาก ID
#     except User.DoesNotExist:
#         return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

#     # ตรวจสอบว่า request มีฟิลด์สถานะหรือไม่
#     status = request.data.get('status')
#     if not status:
#         return Response({'detail': 'Status field is required'}, status=status.HTTP_400_BAD_REQUEST)

#     # อัปเดตสถานะของผู้ใช้
#     user.status = status
#     user.save()

#     return Response({'status': user.status}, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import User, Usersdetail
from rest_framework.permissions import AllowAny

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



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import HotelApproval

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


from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Reservation
from .serializers import ReservationSerializer

@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])  # ✅ ใช้ Token Authentication
@permission_classes([IsAuthenticated])  # ✅ ให้เฉพาะผู้ใช้ที่ล็อกอินแล้วเท่านั้น
def update_reservation_status(request, reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ ตรวจสอบสิทธิ์เฉพาะ admin หรือเจ้าของ
    if not request.user.is_staff and request.user != reservation.pet_owner:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get("status")
    reservation.status = new_status
    reservation.save()

    return Response({"success": "Status updated", "status": new_status})

