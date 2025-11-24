# backend/apps/users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .views import ( 
    UserSignupView, VerifyEmailView, ResendVerificationView, LoginView,
    UserViewSet, LogoutView, DireccionViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'direcciones', DireccionViewSet, basename='direcciones')

urlpatterns = [
     # Endpoints de autenticación / registro
    path('auth/signup/', UserSignupView.as_view(), name='users-signup'),
    path('auth/verify/', VerifyEmailView.as_view(), name='users-verify-email'),            # usado por tasks.reverse(...)
    path('auth/resend-verification/', ResendVerificationView.as_view(), name='users-resend-verification'),

    # Login / logout
    path('auth/login/', LoginView.as_view(), name='users-login'),
    path('auth/logout/', LogoutView.as_view(), name='users-logout'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('', include(router.urls)),
]
