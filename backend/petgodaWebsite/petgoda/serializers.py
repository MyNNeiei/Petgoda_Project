from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken



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


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False)  
    last_name = serializers.CharField(source="user.last_name", required=False)  
    phone_number = serializers.CharField(required=False, allow_null=True)  
    gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)  
    birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")
    profile_pic = serializers.ImageField(required=False, allow_null=True)  # Fixed ImageField issue


    class Meta:
        model = Usersdetail
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'gender', 'profile_pic']


# ✅ Serializer for User Model with Nested Profile Data
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source='usersdetail', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class UsersdetailSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Usersdetail
        fields = ['gender', 'phone_number', 'birth_date']

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'

class ProfileEditSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    email = serializers.EmailField(source="user.email", required=False)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")
    profile_pic = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Usersdetail
        fields = ["first_name", "last_name", "email", "phone_number", "birth_date", "gender", "profile_pic"]

    def update(self, instance, validated_data):
        """
        Updates both the `Usersdetail` model and the linked `User` model.
        """

        # Get associated User model
        user = instance.user

        # Update User model fields using validated_data directly
        user.first_name = validated_data.get('user', {}).get('first_name', user.first_name) # Use .get() to handle missing fields gracefully.
        user.last_name = validated_data.get('user', {}).get('last_name', user.last_name)
        user.email = validated_data.get('user', {}).get('email', user.email)
        user.save()

        # Update Usersdetail fields
        instance.phone_number = validated_data.get('phone_number', instance.phone_number) #Use .get() here too.
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
        instance.save()

        return instance

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'
