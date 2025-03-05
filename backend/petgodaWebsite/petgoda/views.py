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
@permission_classes([AllowAny])  # Allow access to anyone
def hotel_list(request):
    hotels = Hotel.objects.all()  # Get all hotels
    serializer = HotelSerializer(hotels, many=True)  # Serialize data
    return Response(serializer.data)  # Return data in JSON format

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can update the status
def update_hotel_status(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'detail': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get('status')
    if status_value not in ['pending', 'confirmed', 'cancelled']:
        return Response({'detail': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

    hotel.is_verified = status_value == 'confirmed'
    hotel.save()

    return Response({'status': hotel.is_verified}, status=status.HTTP_200_OK)


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
