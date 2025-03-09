from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
# Create your models here.

def profile_upload_path(instance, filename): # เอาไว้ upload รูปโปรไฟล์ เป็นการแปลงนามสกุลไฟล์
    # แยกนามสกุลไฟล์ออกมา
    ext = filename.split('.')[-1]
    # สร้างชื่อไฟล์ใหม่ในรูปแบบ username-originalfilename.extension
    new_filename = f"{instance.user.username}-{filename}"
    return f'profile_pictures/{new_filename}'

class Usersdetail(models.Model):
    class Gender(models.TextChoices):
        M = "M", "ผู้ชาย"
        F = "F", "ผู้หญิง"
        LGBTQ = "LGBTQ", "LGBTQ+"   
        O = "O", "อื่นๆ"

    class Role(models.TextChoices):
        ADMIN = "Admin", "ผู้ดูแลระบบ"
        PETOWNER = "PetOwner", "ผู้ใช้ทั่วไป"
        HOTEL = "Hotel", "โรงแรม"
    
    class Status(models.TextChoices):
        ACTIVE = "Active", "ใช้งานได้"
        BANNED = "Banned", "ถูกแบน"
        PENDING = "Pending", "รอดำเนินการ"

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.O, blank=True, null=True)
    picture = models.ImageField(upload_to=profile_upload_path, blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PETOWNER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Pet(models.Model):
    class PetType(models.TextChoices):
        DOG = "D", "หมา"
        CAT = "C", "แมว"

    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    pettype = models.CharField(max_length=1, choices=PetType.choices) 
    age = models.PositiveIntegerField(null=True, blank=True)
    birth_date = models.DateField()
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, )
    height = models.DecimalField(
        max_digits=5, 
        decimal_places=2, )
    allegic = models.CharField(max_length=255, null=True)
    properties = models.CharField(max_length=255, null=True)
    def __str__(self):
        return f"{self.name} ({self.get_pettype_display()}) - {self.weight} kg"

def hotel_upload_path(instance, filename):
    return f'hotel_img/{instance.name}/{filename}'

class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)  # FK ไปยัง User
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000)
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=30, unique=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    
    address = models.CharField(max_length=255, null=True, blank=True)  # ✅ แก้ไข FK location

    place_id = models.CharField(max_length=1000, unique=True)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    total_review = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2,   # ป้องกันค่าติดลบ
        default=0.0
    )
    imgHotel = models.ImageField(upload_to=hotel_upload_path, default="hotel_img/default_hotel.jpg")



class ImgRoom(models.Model):
    image = models.ImageField(upload_to='room_images/')
    description = models.TextField(blank=True)

class Room(models.Model):
    
    AVAILABILITY_STATUS_CHOICES = [
        ('available', 'Available'),  # พร้อมใช้งาน
        ('partially_reserved', 'Partially Reserved'),  # ถูกจองบางส่วน (ยังรับจองเพิ่มได้)
        ('fully_reserved', 'Fully Reserved'),  # ถูกจองเต็มแล้ว
        ('partially_occupied', 'Partially Occupied'),  # มีสัตว์เลี้ยงเข้าพักแล้ว แต่ยังรับเพิ่มได้
        ('fully_occupied', 'Fully Occupied'),  # มีสัตว์เลี้ยงเข้าพักเต็มความจุแล้ว
        ('maintenance', 'Maintenance'),  # กำลังซ่อมบำรุง
        ('unavailable', 'Unavailable'),  # ไม่พร้อมใช้งานชั่วคราว
    ]
    
    PET_SIZE_CHOICES = [
        ('small', 'Small'),  # ขนาดเล็ก
        ('medium', 'Medium'),  # ขนาดกลาง
        ('large', 'Large'),  # ขนาดใหญ่
        ('all', 'All Sizes'),
    ]
    
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),  # สุนัข
        ('cat', 'Cat'),  # แมว
        ('all', 'All Pets'),  # รับทุกประเภท
    ]
        
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, null=False)
    roomname = models.CharField(max_length=30, null=False)
    size = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    rating_decimal = models.DecimalField(max_digits=3, decimal_places=1, null=False) # เป็นค่า avg
    total_review = models.IntegerField(null=False, default=0.0)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS_CHOICES, default='available', null=False)
    max_pets = models.IntegerField(null=False, default=1)
    current_pets_count_int = models.IntegerField(null=False) # สัตว์เลี้ยงในห้องนี้ปัจจุบันมีกี่ตัวแล้ว
    room_type = models.CharField(max_length=50, null=True) # ex. 'standard', 'suite', 'deluxe'
    allow_pet_size = models.CharField(max_length=20, choices=PET_SIZE_CHOICES, default='small', null=False) # choice
    allow_pet_type = models.CharField(max_length=20, choices=PET_TYPE_CHOICES, default='dog', null=False) # choice
    images = models.ManyToManyField(ImgRoom, related_name='rooms')
    
    # def __str__(self):
    #     return self.roomname
    
class Reservation(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'), # รอดำเนินการ - รอโรงแรมอนุมัติ  
        ('confirmed', 'Confirmed'), # ยืนยันแล้ว ยังไม่ check in
        ('cancelled', 'Cancelled'), # ยกเลิก
        ('completed', 'Completed'), # เสร็จสิ้น: check in แล้ว
    ]
    
    PAYMENT_STATUS_CHOICES = [ # อย่าลืมว่าของเราเป็นการจ่ายที่โรงแรม ฝั่งโรงแรมจะสามารถเปลี่ยนแปลงค่าตรงนี้ได้
        ('unpaid', 'Unpaid'), 
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    pet_owner = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'role': 'PETOWNER'}, null=False) #  เป็นเงื่อนไขที่กำหนดว่าให้เลือกเฉพาะออบเจกต์ที่มีค่า role เท่ากับ 'PETOWNER'
    pet = models.ForeignKey(Pet, on_delete=models.PROTECT, null=False)
    room = models.ForeignKey(Room, on_delete=models.PROTECT, null=False)
    check_in_date = models.DateTimeField(null=True)
    check_out_date = models.DateTimeField(null=True)
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', null=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid', null=False)
    special_request = models.TextField(null=False) # ลูกค้าอยาก note อะไรให้โรงแรมรับทราบไหม
    cancellation_reason = models.TextField(null=False) # เหตุผลว่าถ้าการจองถูกยกเลิก ทำไมถึงยกเลิก ยกเลิกได้เฉพาะ status Pending
    created_at = models.DateTimeField(auto_now_add=True, null=False) # auto_now_add เซ็ตเวลา ครั้งเดียว ตอนสร้างข้อมูล
    updated_at = models.DateTimeField(auto_now=True, null=False) # auto_now อัปเดตเวลา ทุกครั้ง ที่บันทึก

    # def __str__(self):
    #     return f'Reservation by {self.pet_owner} for {self.pet} in Room {self.room}'

class FacilitiesHotel(models.Model):
    hotel = models.OneToOneField("Hotel", on_delete=models.CASCADE)  # เชื่อมกับ Hotel (1:1)

    has_veterinary_services = models.BooleanField(default=False)
    has_grooming_services = models.BooleanField(default=False)
    has_training_services = models.BooleanField(default=False)
    has_swimming_pool = models.BooleanField(default=False)
    has_playground = models.BooleanField(default=False)
    has_outdoor_area = models.BooleanField(default=False)
    has_transport_services = models.BooleanField(default=False)
    has_emergency_services = models.BooleanField(default=False)
    has_pet_friendly_cafe = models.BooleanField(default=False)
    has_pet_spa = models.BooleanField(default=False)
    has_special_diet_options = models.BooleanField(default=False)
    has_24h_support = models.BooleanField(default=False)
    has_group_play_sessions = models.BooleanField(default=False)
    has_pet_taxi_service = models.BooleanField(default=False)
    has_pet_fitness_center = models.BooleanField(default=False)
    has_pet_photography = models.BooleanField(default=False)
    has_pet_party_services = models.BooleanField(default=False)

    def __str__(self):
        return f"Facilities for {self.hotel.name}"

class FacilitiesRoom(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='facilities')
    has_air_conditioning = models.BooleanField(default=False)
    has_cctv = models.BooleanField(default=False)
    has_webcam_monitoring = models.BooleanField(default=False)
    has_pet_food = models.BooleanField(default=False)
    has_toys = models.BooleanField(default=False)
    has_private_space = models.BooleanField(default=False)
    has_pet_bedding = models.BooleanField(default=False)
    has_soundproofing = models.BooleanField(default=False)
    has_water_dispenser = models.BooleanField(default=False)
    has_emergency_button = models.BooleanField(default=False)
    has_natural_light = models.BooleanField(default=False)
    has_flexible_checkin = models.BooleanField(default=False)

    def __str__(self):
        return f"Facilities for Room: {self.room.roomname}"

class HotelApproval(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "รอดำเนินการ"
        CONFIRMED = "confirmed", "ยืนยันแล้ว"
        CANCELLED = "cancelled", "ถูกยกเลิก"

    hotel = models.ForeignKey("Hotel", on_delete=models.CASCADE, related_name="approvals")  # FK ไปยัง Hotel
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # ผู้อนุมัติ (อาจเป็น Null)
    
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    
    reviewed_at = models.DateTimeField(auto_now=True)  # เวลาที่มีการตรวจสอบ
    reason = models.TextField(blank=True, null=True)  # เหตุผลถ้าไม่ผ่าน

    def __str__(self):
        return f"Approval for {self.hotel.name} - {self.get_status_display()}"

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('booking_confirmation', 'Booking Confirmation'),  # ยืนยันการจองสำเร็จ (ลูกค้า)
        ('booking_cancellation', 'Booking Cancellation'),  # ยกเลิกการจอง (ลูกค้า)
        ('new_booking_request', 'New Booking Request'),  # การจองใหม่ (สำหรับโรงแรม)
        ('promotion', 'Hotel Promotion'),  # โปรโมชั่นโรงแรม (ลูกค้า)
    ]
    
    user = models.ForeignKey(Usersdetail, on_delete=models.PROTECT, null=False)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    notification_type = models.CharField(
        max_length=30, 
        choices=NOTIFICATION_TYPE_CHOICES, 
        default='booking_confirmation'
    )

