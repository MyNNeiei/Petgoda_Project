from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
from petgoda.views import update_hotel_reason  # ✅ ต้อง import views เข้ามาด้วย!

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.user_list, name='user_list'),  
    path('hotels/', views.hotel_list, name='hotel-list'),  
    # path('reservations/', views.reservation_list, name="reservation_list"),
    path('profile/edit/', views.edit_profile_view, name='profile_edit'),
    path('pets/create/', views.pet_list_create, name="pet_list_create"),
    path('pets/', views.pet_list_views, name="pet_list_views"),
    # path('reservations/<int:reservation_id>/', views.update_reservation_status, name="update_reservation"),
    path("reservations/", views.reservation_list, name="reservation-list"),
    path("reservations/<int:id>/", views.reservation_detail, name="reservation-detail"),
    path('users/<int:user_id>/update_status/', views.update_user_status, name='update_user_status'),  
    path('hotels/<int:hotel_id>/update_status/', views.update_hotel_status, name='update_hotel_status'),
    path('reservations/<int:reservation_id>/update_status/', views.update_reservation_status, name='update_reservation_status'),
    path('hotels/<int:hotel_id>/update_reason/', update_hotel_reason, name='update_hotel_reason'),  # ✅ ลบ "api/" ซ้ำ
]
# ✅ Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
