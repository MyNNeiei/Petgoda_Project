from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.user_list, name='user_list'),  # ดึงข้อมูล User ทั้งหมด
    # path('hotels/', views.hotel_detail, name='hotel-list'),
    path('hotels/', views.hotel_list, name='hotel-list'),  # ใช้ hotel_list สำหรับดึงข้อมูลทั้งหมด
    # path('users/<int:id>/', views.user_detail, name='user_detail'),  # ดึงข้อมูล User รายบุคคล
    path("reserve/", views.reservation_list, name="reservation_list"),
    path('profile/edit/', views.edit_profile_view, name='profile_edit'),
    path("api/pets/create/", views.pet_list_create, name="pet_list_create"),
    path("api/pets/", views.pet_list_views, name="pet_list_views"),
    path("reserve/<int:reservation_id>/", views.update_reservation_status, name="update_reservation"),
    # path('adminPage/', views.admin_page_view, name='adminPage'),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
