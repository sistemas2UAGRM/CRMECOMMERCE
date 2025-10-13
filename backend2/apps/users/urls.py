# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserRegistrationView, AdminUserRegistrationView, LoginView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('admin-register/', AdminUserRegistrationView.as_view(), name='admin-user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('', include(router.urls)),
]
