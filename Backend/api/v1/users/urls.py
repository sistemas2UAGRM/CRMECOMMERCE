# api/v1/users/urls.py

"""
📚 MICROCONCEPTOS - CONFIGURACIÓN DE URLs EN DRF

Las URLs en DRF se pueden configurar de varias maneras:

1. ROUTERS: Para ViewSets, generan automáticamente las URLs CRUD
2. path(): Para vistas individuales como APIView
3. include(): Para incluir URLs de otras apps

Tipos de routers:
- DefaultRouter: Incluye una vista raíz de la API
- SimpleRouter: Más básico, sin vista raíz

Patrones de URL:
- /users/ -> UserViewSet.list()
- /users/{id}/ -> UserViewSet.retrieve()
- /users/profile/ -> UserViewSet.profile() (acción personalizada)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegistrationView, AdminUserRegistrationView, LoginView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # Endpoints de autenticación (no requieren ViewSet)
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('admin-register/', AdminUserRegistrationView.as_view(), name='admin-user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    
    # ViewSet URLs (incluye todas las acciones CRUD + personalizadas)
    path('', include(router.urls)),
]

"""
📝 MICROCONCEPTO: URLs generadas automáticamente

El router genera estas URLs automáticamente:

CRUD básico:
- GET /api/v1/users/ -> UserViewSet.list()
- POST /api/v1/users/ -> UserViewSet.create()
- GET /api/v1/users/{id}/ -> UserViewSet.retrieve()
- PUT /api/v1/users/{id}/ -> UserViewSet.update()
- PATCH /api/v1/users/{id}/ -> UserViewSet.partial_update()
- DELETE /api/v1/users/{id}/ -> UserViewSet.destroy()

Acciones personalizadas:
- GET/PUT/PATCH /api/v1/users/profile/ -> UserViewSet.profile()
- GET /api/v1/users/search/ -> UserViewSet.search()
- GET /api/v1/users/active/ -> UserViewSet.active()
- GET /api/v1/users/by-role/{role_name}/ -> UserViewSet.by_role()
- GET /api/v1/users/stats/ -> UserViewSet.stats()

Endpoints manuales:
- POST /api/v1/users/register/ -> UserRegistrationView
- POST /api/v1/users/admin-register/ -> AdminUserRegistrationView
- POST /api/v1/users/login/ -> LoginView
"""
