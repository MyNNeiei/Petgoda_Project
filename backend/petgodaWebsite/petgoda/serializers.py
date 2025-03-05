# from rest_framework import serializers
# from .models import *
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import Usersdetail


# class RegisterSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True)
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, min_length=8)
#     confirm_password = serializers.CharField(write_only=True, min_length=8)
    
#     # userdetail
#     gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
#     phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password', 
#                   'gender', 'phone_number', 'birth_date']

#     def validate(self, data):
#         if data['password'] != data['confirm_password']:
#             raise serializers.ValidationError({'password': 'Passwords do not match'})
#         if User.objects.filter(email=data['email']).exists():
#             raise serializers.ValidationError({'email': 'This email is already in use'})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirm_password')  # เอาออกก่อนบันทึกข้อมูล

#         # แยกข้อมูลของ Usersdetail
#         gender = validated_data.pop('gender', Usersdetail.Gender.O)
#         phone_number = validated_data.pop('phone_number', None)
#         birth_date = validated_data.pop('birth_date', None)

#         # สร้าง User
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name'],
#             password=validated_data['password']
#         )

#         # สร้าง Usersdetail พร้อม role เป็น PETOWNER
#         Usersdetail.objects.create(
#             user=user,
#             role=Usersdetail.Role.PETOWNER,
#             gender=gender,
#             phone_number=phone_number,
#             birth_date=birth_date
#         )
#         print(user)
#         return user

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(username=data.get('username'), password=data.get('password'))
#         if not user:
#             raise serializers.ValidationError('Invalid username or password')
        
#         # Ensure Usersdetail exists
#         Usersdetail.objects.get_or_create(user=user, defaults={
#             'role': Usersdetail.Role.PETOWNER,
#             'gender': Usersdetail.Gender.O
#         })
        
#         data['user'] = user
#         return data


# class ProfileSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source="user.username", read_only=True)
#     email = serializers.EmailField(source="user.email", read_only=True)
#     first_name = serializers.CharField(source="user.first_name", required=False)  
#     last_name = serializers.CharField(source="user.last_name", required=False)  
#     phone_number = serializers.CharField(required=False, allow_null=True)  
#     gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)  
#     birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")
#     profile_pic = serializers.ImageField(required=False, allow_null=True)  # Fixed ImageField issue


#     class Meta:
#         model = Usersdetail
#         fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'birth_date', 'gender', 'profile_pic']


# # ✅ Serializer for User Model with Nested Profile Data
# class UserSerializer(serializers.ModelSerializer):
#     profile = ProfileSerializer(source='usersdetail', read_only=True)

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'profile']

# class UsersdetailSerializer(serializers.ModelSerializer):
#     gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
#     phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#     birth_date = serializers.DateField(required=False, allow_null=True)

#     class Meta:
#         model = Usersdetail
#         fields = ['gender', 'phone_number', 'birth_date']

# class PetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pet
#         fields = '__all__'

# class UsersdetailSerializer(serializers.ModelSerializer):
#     full_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Usersdetail
#         fields = ['id', 'user', 'birth_date', 'phone_number', 'gender', 'role', 'created_at', 'location', 'full_name']

#     def get_full_name(self, obj):
#         return obj.get_full_name()


# class ProfileEditSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(source="user.first_name", required=False)
#     last_name = serializers.CharField(source="user.last_name", required=False)
#     email = serializers.EmailField(source="user.email", required=False)
#     phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#     gender = serializers.ChoiceField(choices=Usersdetail.Gender.choices, required=False, allow_null=True)
#     birth_date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d")
#     profile_pic = serializers.ImageField(required=False, allow_null=True)

#     class Meta:
#         model = Usersdetail
#         fields = ["first_name", "last_name", "email", "phone_number", "birth_date", "gender", "profile_pic"]

#     def update(self, instance, validated_data):
#         """
#         Updates both the `Usersdetail` model and the linked `User` model.
#         """

#         # Get associated User model
#         user = instance.user

#         # Update User model fields using validated_data directly
#         user.first_name = validated_data.get('user', {}).get('first_name', user.first_name) # Use .get() to handle missing fields gracefully.
#         user.last_name = validated_data.get('user', {}).get('last_name', user.last_name)
#         user.email = validated_data.get('user', {}).get('email', user.email)
#         user.save()

#         # Update Usersdetail fields
#         instance.phone_number = validated_data.get('phone_number', instance.phone_number) #Use .get() here too.
#         instance.gender = validated_data.get('gender', instance.gender)
#         instance.birth_date = validated_data.get('birth_date', instance.birth_date)
#         instance.profile_pic = validated_data.get('profile_pic', instance.profile_pic)
#         instance.save()

#         return instance

# class HotelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Hotel
#         fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     # ใช้ source เพื่อดึงข้อมูลจาก Usersdetail
#     phone_number = serializers.CharField(source='usersdetail.phone_number', read_only=True)
#     birth_date = serializers.DateField(source='usersdetail.birthdate', read_only=True)

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'is_staff', 'is_active', 'date_joined', 'phone_number', 'birth_date']

# class HotelSerializer(serializers.ModelSerializer):
#     # ถ้าคุณต้องการแสดงข้อมูลของ Location หรือ User สามารถใช้ Serializer ของโมเดลเหล่านั้นได้
#     location = serializers.StringRelatedField()  # ถ้าต้องการแค่ชื่อ/ข้อมูลในที่เก็บของ Location
#     owner = serializers.StringRelatedField()  # เช่นเดียวกับ owner ถ้าคุณต้องการแค่ชื่อผู้ใช้งาน

#     class Meta:
#         model = Hotel
#         fields = '__all__'  # ใช้ฟิลด์ทั้งหมดจากโมเดล Hotel

from rest_framework import serializers
from .models import *
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator

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

class PetSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.user.username", read_only=True)  # ✅ Show pet owner's username

    class Meta:
        model = Pet
        fields = ["id", "name", "pettype", "age", "birth_date", "weight", "height", "allegic", "properties", "owner", "owner_name"]
        read_only_fields = ["owner"]  # ✅ Prevent manual owner assignment

