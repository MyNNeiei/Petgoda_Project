from decimal import Decimal
from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from rest_framework import serializers
from petgoda.models import Reservation

from rest_framework import serializers
from .models import Reservation

from rest_framework import serializers
from .models import Reservation

from rest_framework import viewsets


class ReservationSerializer(serializers.ModelSerializer):
    pet_owner = serializers.CharField(source="pet_owner.username")
    pet = serializers.SerializerMethodField()
    room = serializers.CharField(source="room.roomname")
    check_in_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)
    check_out_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)
    total_price = serializers.SerializerMethodField()  # ✅ เพิ่ม field นี้

    class Meta:
        model = Reservation
        fields = "__all__"
        
    def get_total_price(self, obj):
        return obj.totalprice 

    def get_pet(self, obj):
        return f"{obj.pet.name} ({obj.pet.get_pettype_display()}) - {obj.pet.weight} kg"
    
    


from datetime import date
from django.shortcuts import get_object_or_404
# ✅ ใช้ UsersdetailSerializer ให้แสดงข้อมูลของผู้ใช้
class UsersdetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    # location = LocationSerializer(read_only=True)  # ✅ ใช้ LocationSerializer

    class Meta:
        model = Usersdetail
        fields = ['id', 'user', 'birth_date', 'phone_number', 'gender', 'role', 'created_at', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name()

# ✅ ใช้ UsersdetailSerializer ให้ User สามารถดึงข้อมูล profile ได้
class UserSerializer(serializers.ModelSerializer):
    profile = UsersdetailSerializer(source='usersdetail', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

# # ✅ ใช้ LocationSerializer แสดงข้อมูลพิกัดของโรงแรม
# class HotelSerializer(serializers.ModelSerializer):
#     location = LocationSerializer(read_only=True)
#     owner = serializers.StringRelatedField()

#     class Meta:
#         model = Hotel
#         fields = '__all__'

# ✅ ใช้ RegisterSerializer เพื่อให้สามารถลงทะเบียนผู้ใช้ใหม่
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    # userdetail
    gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 
                  'gender', 'phone_number', 'birth_date']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match'})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'This email is already in use'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # เอาออกก่อนบันทึกข้อมูล

        # แยกข้อมูลของ Usersdetail
        gender = validated_data.pop('gender', Usersdetail.Gender.O)
        phone_number = validated_data.pop('phone_number', None)
        birth_date = validated_data.pop('birth_date', None)

        # สร้าง User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        # สร้าง Usersdetail พร้อม role เป็น PETOWNER
        Usersdetail.objects.create(
            user=user,
            role=Usersdetail.Role.PETOWNER,
            gender=gender,
            phone_number=phone_number,
            birth_date=birth_date
        )
        return user

# ✅ ใช้ LoginSerializer เพื่อให้สามารถเข้าสู่ระบบได้
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError('Invalid username or password')
        
        # Ensure Usersdetail exists
        Usersdetail.objects.get_or_create(user=user, defaults={
            'role': Usersdetail.Role.PETOWNER,
            'gender': Usersdetail.Gender.O
        })
        
        data['user'] = user
        return data


def profile_upload_path(instance, filename):
    """
    Generate upload path for profile pictures.
    """
    return f'profile_pictures/{instance.user.username}/{filename}'


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='usersdetail.phone_number', required=False, allow_null=True)
    address = serializers.CharField(source='usersdetail.address', required=False, allow_null=True)

    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This email is already registered."
        )]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'phone_number', 'address','is_active']
        # Removed 'email' from read_only_fields to allow updating.  Email uniqueness is already enforced.
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'username': {'required': False},  # Make username optional during update
        }

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_phone_number(self, value):
        if value:
            # ลบช่องว่างและตัวอักษรพิเศษออก
            cleaned_number = ''.join(filter(str.isdigit, value))

            # ตรวจสอบความยาวเบอร์โทร
            if len(cleaned_number) != 10:
                raise serializers.ValidationError("Phone number must be 10 digits")

            # ตรวจสอบว่าขึ้นต้นด้วย 0
            if not cleaned_number.startswith('0'):
                raise serializers.ValidationError("Phone number must start with 0")

            # ส่งคืนในรูปแบบที่เป็นเลขล้วนๆ (ไม่มีเครื่องหมาย -)
            return cleaned_number
        return value
    
    def validate_phone_number(self, value):
        if value:
            # ลบช่องว่างและตัวอักษรพิเศษออก
            cleaned_number = ''.join(filter(str.isdigit, value))

            # ตรวจสอบความยาวเบอร์โทร
            if len(cleaned_number) != 10:
                raise serializers.ValidationError("Phone number must be 10 digits")

            # ตรวจสอบว่าขึ้นต้นด้วย 0
            if not cleaned_number.startswith('0'):
                raise serializers.ValidationError("Phone number must start with 0")

            # ส่งคืนในรูปแบบที่เป็นเลขล้วนๆ (ไม่มีเครื่องหมาย -)
            return cleaned_number
        return value
    def validate_birth_date(self, value):
        today = date.today()

        # Ensure the birth date is not in the future
        if value > today:
            raise serializers.ValidationError("Birth date cannot be in the future.")

        # Ensure the user is at least 18 years old
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("You must be at least 18 years old.")

        return value

    def get_profile_picture(self, obj):
        try:  # Handle the case where the Usersdetail might not exist yet
            if obj.usersdetail.picture:
                request = self.context.get('request')
                picture = obj.usersdetail.picture
                if isinstance(picture, str):
                    picture_url = picture
                else:
                    picture_url = picture.url
                if request:
                    return request.build_absolute_uri(picture_url)
                return picture_url
            return None
        except Usersdetail.DoesNotExist:
            return None

    def update(self, instance, validated_data):
        # Handle User fields
        for attr, value in validated_data.items():
            if attr in ('first_name', 'last_name', 'username', 'email'):  # Update allowed User fields
                setattr(instance, attr, value)
        instance.save()

        # Handle Usersdetail fields
        usersdetail_data = validated_data.pop('usersdetail', {})  # Use 'usersdetail' key
        try:
            usersdetail = instance.usersdetail  # Get existing Usersdetail instance
        except Usersdetail.DoesNotExist:
            usersdetail = Usersdetail.objects.create(user=instance)  # Create if it doesn't exist

        if usersdetail_data:  # Only update if data is provided
            for attr, value in usersdetail_data.items():
                setattr(usersdetail, attr, value)  # Directly update attributes

            usersdetail.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        #Ensure that profile_picture is always a URL
        if representation['profile_picture']:
            return representation
        else:
            representation['profile_picture'] = None # Or a default image URL
            return representation


class UsersdetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usersdetail
        fields = ['birth_date', 'phone_number', 'gender', 'picture', 'role', 'address']


class FacilitiesHotelSerializer(serializers.ModelSerializer):
    """✅ Serializes hotel facilities"""

    class Meta:
        model = FacilitiesHotel
        fields = "__all__"  # ✅ Includes all facility fields
        read_only_fields = ["hotel"]

class FacilitiesRoomSerializer(serializers.ModelSerializer):
    """Serializes facilities available in a room"""
    class Meta:
        model = FacilitiesRoom
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)  # ✅ Display hotel name
    facilities = FacilitiesRoomSerializer(read_only=True)  # ✅ Include room facilities

    class Meta:
        model = Room
        fields = [
            "id", "hotel", "hotel_name", "roomname", "size", "price_per_night", 
            "rating_decimal", "total_review", "availability_status", "max_pets", 
            "current_pets_count_int", "room_type", "allow_pet_size", "allow_pet_type", 
            "facilities"
        ]
        read_only_fields = ["hotel"]  # ✅ Prevent setting hotel manually

    def validate_price_per_night(self, value):
        """Ensure price is not negative"""
        if value < 0:
            raise serializers.ValidationError("Price per night must be a positive value.")
        return value

def hotel_upload_path(instance, filename):
    return f'hotel_img/{instance.name}/{filename}'

class HotelSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = '__all__'
        extra_kwargs = {
            'owner': {'required': False}  # กำหนดให้ owner ไม่จำเป็นต้องส่งมา
        }

    def get_image_url(self, obj):
        if hasattr(obj, "imgHotel") and obj.imgHotel:
            request = self.context.get('request')
            image = obj.imgHotel
            image_url = image if isinstance(image, str) else image.url
            return request.build_absolute_uri(image_url) if request else image_url
        return None

    def validate_phone(self, value):
        """Ensure phone number is valid (10 digits, starts with 0)"""
        cleaned_number = ''.join(filter(str.isdigit, value))
        if len(cleaned_number) != 10 or not cleaned_number.startswith('0'):
            raise serializers.ValidationError("Phone number must be 10 digits and start with 0")
        return cleaned_number
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ["id", "name", "pettype", "age", "birth_date", "weight", "height", "allegic", "properties", "owner"]
        read_only_fields = ["owner"]  # ✅ Prevent manual owner assignment

class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['status']  # แค่ฟิลด์สถานะที่ต้องการอัปเดต
        def validate_birth_date(self, value):
            
            today = date.today()

            # Ensure the birth date is not in the future
            if value > today:
                raise serializers.ValidationError("Birth date cannot be in the future.")

            # Ensure the user is at least 18 years old
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 18:
                raise serializers.ValidationError("You must be at least 18 years old.")
            return value

class PetDeleteSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField(required=True)

    def validate_pet_id(self, value):
        """Ensure pet exists and belongs to the requesting user"""
        request = self.context["request"]
        pet = get_object_or_404(Pet, id=value, owner=request.user)
        return pet  # Return the pet object itself

    def delete(self):
        """Delete the validated pet"""
        pet = self.validated_data["pet_id"]
        pet.delete()
        return {"detail": "Pet deleted successfully"}


class ImgRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImgRoom
        fields = ["id", "image", "description"]

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
