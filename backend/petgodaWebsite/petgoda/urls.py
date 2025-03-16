from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
from petgoda.views import update_hotel_reason

urlpatterns = [
    path('profile/', views.profile_view, name='profile_view'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.user_list, name='user_list'),  
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
    path('users/', views.user_list, name='user_list'),  # ดึงข้อมูล User ทั้งหมด
    #hotels reserve
    # path("hotels/<int:hotel_id>", views.view_hotel_details, name="view_hotel_details"),
    path("hotels/<int:hotel_id>/", views.view_hotel_details, name="view_hotel_details"),

    #hotel admin
    path("hotels/create/", views.create_hotel, name="create_hotel"),
    path("hotels/<int:hotel_id>/delete/", views.delete_hotel, name="delete_hotel"),
    path("hotels/", views.view_all_hotels, name="view_all_hotels_manage"),
    path('hotels/edit/<int:hotel_id>', views.update_hotel_details, name='manage_get_hotel_details'),
    path('hotels/<int:hotel_id>/rooms/', views.hotel_rooms, name='hotel_rooms'),
    path("hotels/rooms/<int:hotel_id>/create/", views.create_room, name="create_room"),
    path("hotels/rooms/<int:hotel_id>/update/", views.update_room, name="update_room"),
    path("hotels/<int:hotel_id>/facilities/", views.get_hotel_facilities, name="get_hotel_facilities"),
    path("hotels/facilities/<int:hotel_id>/update", views.update_hotel_facilities, name="update_hotel_facilities"),
    #profile
    path("reservations/create/", views.create_reservation, name='reserve_hotels'),
    path("user/", views.get_user_info, name="get_user_info"),
    path('profile/edit/', views.edit_profile_view, name='profile_edit'),
    path("pet/create/", views.pet_list_create, name="pet_list_create"),
    path("pet/delete/<int:pet_id>", views.pet_list_delete, name="pet_list_delete"),
    path("pet/", views.pet_list_views, name="pet_list_views"),
    # path("reserve/<int:reservation_id>/", views.update_reservation_status, name="update_reservation"),
    path("reservations/check_availability/", views.check_room_availability, name="check_room_availability"),
    path("users/me/", views.get_current_user, name="get_current_user"),  # ✅ เพิ่ม API ใหม่

]
# ✅ Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
