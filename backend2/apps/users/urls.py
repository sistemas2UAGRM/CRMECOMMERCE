# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import (UserRegistrationView, AdminUserRegistrationView, 
    LoginView, UserViewSet, LogoutView, DireccionViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'direcciones', DireccionViewSet, basename='direcciones')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('admin-register/', AdminUserRegistrationView.as_view(), name='admin-user-register'),
    path('login/', LoginView.as_view(), name='user-login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('', include(router.urls)),
]
