from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('profile/<int:id>/', views.profile_view, name='profile_view'),

    # path("profile/edit/", ProfileEditViewAPI.as_view(), name="profile_edit"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path("reserve/", views.reservation_list, name="reservation_list"),
    path("reserve/<int:reservation_id>/", views.update_reservation_status, name="update_reservation"),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
