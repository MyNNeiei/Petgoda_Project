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
    #hotels reserve
    path("hotels/", views.view_all_hotels, name="view_all_hotels"),
    path("hotels/<int:hotel_id>", views.view_hotel_details, name="view_hotel_details"),
    #hotel admin
    path("hotels/create/", views.create_hotel, name="create_hotel"),
    path("hotels/<int:hotel_id>/delete/", views.delete_hotel, name="delete_hotel"),
    path("hotels/", views.view_all_hotels, name="view_all_hotels_manage"),
    path('hotels/edit/<int:hotel_id>', views.update_hotel_details, name='manage_get_hotel_details'),
    path('hotels/<int:hotel_id>/rooms/', views.hotel_rooms, name='hotel_rooms'),
    path("hotels/rooms/<int:hotel_id>/create/", views.create_room, name="create_room"),
    path('hotels/<int:hotel_id>/facilities/', views.get_hotel_facilities, name='hotel_facilities'),
    path("hotels/<int:hotel_id>/facilities/update/", views.update_hotel_facilities, name="update_hotel_facilities"),
    #profile
    path('profile/edit/', views.edit_profile_view, name='profile_edit'),
    path("pet/create/", views.pet_list_create, name="pet_list_create"),
    path("pet/delete/<int:pet_id>", views.pet_list_delete, name="pet_list_delete"),
    path("pet/", views.pet_list_views, name="pet_list_views"),
    path("reserve/<int:reservation_id>/", views.update_reservation_status, name="update_reservation"),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
