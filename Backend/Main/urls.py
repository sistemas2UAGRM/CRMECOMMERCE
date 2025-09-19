"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CRM & E-COMMERCE API - Sprint 1",
        default_version='v1',
        description="""
        ## 🚀 API REST Completa para Sistema CRM+Ecommerce
        
        ### **Módulos Implementados:**
        - 👥 **USUARIOS**: Autenticación JWT, perfiles, búsquedas
        - 🔐 **CRM**: Roles jerárquicos, permisos granulares
        - 📊 **BITÁCORA**: Auditoría automática, estadísticas
        - 🛍️ **E-COMMERCE**: Catálogo, carritos, gestión de stock
        
        ### **Autenticación:**
        1. Hacer login en `/api/v1/users/login/`
        2. Copiar el `access_token` 
        3. Hacer clic en **"Authorize"** 🔒
        4. Introducir: `Bearer tu_token_aquí`
        
        ### **Roles del Sistema:**
        - 🔴 **Administrador**: Acceso total
        - 🟡 **Supervisor** (empleadonivel1): Gestión de equipo
        - 🟢 **Vendedor** (empleadonivel2): Operaciones de venta  
        - 🔵 **Cliente**: Acceso básico
        """,
        terms_of_service="https://tu-empresa.com/terms/",
        contact=openapi.Contact(email="admin@empresa.com", name="Soporte API"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #URLs de Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # URLs de la API
    path('api/v1/', include('api.v1.urls')),
    
]
