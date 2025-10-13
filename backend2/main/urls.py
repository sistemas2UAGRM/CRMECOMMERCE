from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="CRM + E-COMMERCE API",
        default_version='v1',
        description="API del sistema CRM + E-COMMERCE",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/users/', include('apps.users.urls')),
    path('api/productos/', include('apps.ecommerce.productos.urls')),
]
