from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator


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
        print(user)
        return user

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


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='profile.phone_number', required=False, allow_null=True)

    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message="This email is already registered."
        )]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'phone_number', 'is_active']
        read_only_fields = ['email']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
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
            
            # ส่งคืนในรูปแบบที่ต้องการ
            return f"{cleaned_number[0:3]}-{cleaned_number[3:6]}-{cleaned_number[6:]}"
        return value
    
    def get_profile_picture(self, obj):
        if obj.profile.picture:
            request = self.context.get('request')
            picture_url = obj.profile.picture.url

            if request:
                return request.build_absolute_uri(picture_url)
            return picture_url
        
        return None

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile = instance.profile
        if profile_data:
            if 'picture' in profile_data:
                profile.picture = profile_data['picture']
            if 'phone_number' in profile_data:
                profile.phone_number = profile_data['phone_number']
            profile.save()

        return instance

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['latitude', 'longitude']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usersdetail
        fields = ['picture']


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class ReservationSerializer(serializers.ModelSerializer):
    pet_owner_name = serializers.CharField(source="pet_owner.username", read_only=True)
    pet_name = serializers.CharField(source="pet.name", read_only=True)
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Reservation
        fields = "__all__"
