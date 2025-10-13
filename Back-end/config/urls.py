from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('api.users.user.urls')),
    path('api/ecommerce/', include('api.ecommerce.category.urls')),
    path('api/ecommerce/', include('api.ecommerce.product.urls')),
    path('api/', include('api.bitacora.urls')),
]
