from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.password_validation import validate_password
from .models import *
from .serializers import *
from rest_framework import generics
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

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

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request, id=None):
    if request.method == 'GET':
        try:
            if id:  # Fetch another user's profile if `id` is provided
                profile = Usersdetail.objects.get(user__id=id)
            else:  # Fetch the current user's profile
                profile = request.user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'PUT':
        try:
            profile = request.user.profile  # Check if a profile already exists
            serializer = ProfileSerializer(profile, data=request.data, partial=True)  # Update existing profile
        except ObjectDoesNotExist:
            serializer = ProfileSerializer(data=request.data)  # Create new profile

        if serializer.is_valid():
            serializer.save(user=request.user)  # Ensure profile is linked to user
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


@api_view(['GET'])
@permission_classes([AllowAny])  # อนุญาตให้ทุกคนเข้าถึง
def hotel_list(request):
    hotels = Hotel.objects.all()  # ดึงข้อมูลโรงแรมทั้งหมด
    serializer = HotelSerializer(hotels, many=True)  # ทำการ serialize ข้อมูลทั้งหมด
    return Response(serializer.data)  # ส่งกลับข้อมูลทั้งหมดในรูปแบบ JSON
