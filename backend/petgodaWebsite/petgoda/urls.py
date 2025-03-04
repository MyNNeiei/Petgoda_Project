from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path("profile/", ProfileViewAPI.as_view(), name="profile"),
    # path("profile/edit/", ProfileEditViewAPI.as_view(), name="profile_edit"),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('adminPage/', views.admin_page_view, name='adminPage'),
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
