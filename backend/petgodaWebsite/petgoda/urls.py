from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('profiles/<int:id>/', views.profile_view, name='profile_view'),

    # path("profile/edit/", ProfileEditViewAPI.as_view(), name="profile_edit"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.user_list, name='user_list'),  # ดึงข้อมูล User ทั้งหมด
    # path('hotels/', views.hotel_detail, name='hotel-list'),
    path('hotels/', views.hotel_list, name='hotel-list'),  # ใช้ hotel_list สำหรับดึงข้อมูลทั้งหมด
    # path('users/<int:id>/', views.user_detail, name='user_detail'),  # ดึงข้อมูล User รายบุคคล
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
